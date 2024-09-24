# Copyright (c) 2012-2013 Mitch Garnaat http://garnaat.org/
# Copyright 2012-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import base64
import calendar
import datetime
import functools
import hmac
import logging
import time
from email.utils import formatdate
from hashlib import sha256

from botocore.compat import (
    MD5_AVAILABLE,
    HTTPHeaders,
    encodebytes,
    ensure_unicode,
    json,
    parse_qs,
    quote,
    urlsplit,
    urlunsplit,
)
from botocore.exceptions import (
    NoAuthTokenError,
    NoCredentialsError,
    UnknownSignatureVersionError,
    UnsupportedSignatureVersionError,
)
from botocore.utils import (
    is_valid_ipv6_endpoint_url,
    normalize_url_path,
    percent_encode_sequence,
)

logger = logging.getLogger(__name__)


EMPTY_SHA256_HASH = (
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
# This is the buffer size used when calculating sha256 checksums.
# Experimenting with various buffer sizes showed that this value generally
# gave the best result (in terms of performance).
PAYLOAD_BUFFER = 1024 * 1024
ISO8601 = '%Y-%m-%dT%H:%M:%SZ'
SIGV4_TIMESTAMP = '%Y%m%dT%H%M%SZ'
SIGNED_HEADERS_BLACKLIST = [
    'expect',
    'user-agent',
    'x-amzn-trace-id',
]
UNSIGNED_PAYLOAD = 'UNSIGNED-PAYLOAD'
STREAMING_UNSIGNED_PAYLOAD_TRAILER = 'STREAMING-UNSIGNED-PAYLOAD-TRAILER'


def _host_from_url(url):
    # Given URL, derive value for host header. Ensure that value:
    # 1) is lowercase
    # 2) excludes port, if it was the default port
    # 3) excludes userinfo
    url_parts = urlsplit(url)
    host = url_parts.hostname  # urlsplit's hostname is always lowercase
    if is_valid_ipv6_endpoint_url(url):
        # Enclose IPv6 Literal addresses in
        # brackets as per RFC 3986 3.2.2.
        host = f'[{host}]'

    default_ports = {
        'http': 80,
        'https': 443
    }
    if url_parts.port is not None:
        if url_parts.port != default_ports.get(url_parts.scheme):
            host = '%s:%d' % (host, url_parts.port)
    return host


def _get_body_as_dict(request):
    # For query services, request.data is form-encoded and is already a
    # dict, but for other services such as rest-json it could be a json
    # string or bytes. In those cases we attempt to load the data as a
    # dict.
    data = request.data
    if isinstance(data, bytes):
        data = json.loads(data.decode('utf-8'))
    elif isinstance(data, str):
        data = json.loads(data)
    return data


class BaseSigner(object):
    REQUIRES_REGION = False
    REQUIRES_TOKEN = False

    def add_auth(self, request):
        raise NotImplementedError("add_auth")


class TokenSigner(BaseSigner):
    REQUIRES_TOKEN = True
    """
    Signers that expect an authorization token to perform the authorization
    """

    def __init__(self, auth_token):
        self.auth_token = auth_token


class SigV2Auth(BaseSigner):
    """
    Sign a request with Signature V2.
    """

    def __init__(self, credentials):
        self.credentials = credentials

    def calc_signature(self, request, params):
        logger.debug("Calculating signature using v2 auth.")
        split = urlsplit(request.url)
        path = split.path
        if len(path) == 0:
            path = '/'
        string_to_sign = '%s\n%s\n%s\n' % (request.method,
                                           split.netloc,
                                           path)
        lhmac = hmac.new(self.credentials.secret_key.encode('utf-8'),
                         digestmod=sha256)
        pairs = []
        for key in sorted(params):
            # Any previous signature should not be a part of this
            # one, so we skip that particular key. This prevents
            # issues during retries.
            if key == 'Signature':
                continue
            value = str(params[key])
            pairs.append(quote(key.encode('utf-8'), safe='') + '=' +
                         quote(value.encode('utf-8'), safe='-_~'))
        qs = '&'.join(pairs)
        string_to_sign += qs
        logger.debug('String to sign: %s', string_to_sign)
        lhmac.update(string_to_sign.encode('utf-8'))
        b64 = base64.b64encode(lhmac.digest()).strip().decode('utf-8')
        return (qs, b64)

    def add_auth(self, request):
        # The auth handler is the last thing called in the
        # preparation phase of a prepared request.
        # Because of this we have to parse the query params
        # from the request body so we can update them with
        # the sigv2 auth params.
        if self.credentials is None:
            raise NoCredentialsError()
        if request.data:
            # POST
            params = request.data
        else:
            # GET
            params = request.params
        params['AWSAccessKeyId'] = self.credentials.access_key
        params['SignatureVersion'] = '2'
        params['SignatureMethod'] = 'HmacSHA256'
        params['Timestamp'] = time.strftime(ISO8601, time.gmtime())
        if self.credentials.token:
            params['SecurityToken'] = self.credentials.token
        qs, signature = self.calc_signature(request, params)
        params['Signature'] = signature
        return request


class SigV3Auth(BaseSigner):
    def __init__(self, credentials):
        self.credentials = credentials

    def add_auth(self, request):
        if self.credentials is None:
            raise NoCredentialsError()
        if 'Date' in request.headers:
            del request.headers['Date']
        request.headers['Date'] = formatdate(usegmt=True)
        if self.credentials.token:
            if 'X-Amz-Security-Token' in request.headers:
                del request.headers['X-Amz-Security-Token']
            request.headers['X-Amz-Security-Token'] = self.credentials.token
        new_hmac = hmac.new(self.credentials.secret_key.encode('utf-8'),
                            digestmod=sha256)
        new_hmac.update(request.headers['Date'].encode('utf-8'))
        encoded_signature = encodebytes(new_hmac.digest()).strip()
        signature = ('AWS3-HTTPS AWSAccessKeyId=%s,Algorithm=%s,Signature=%s' %
                     (self.credentials.access_key, 'HmacSHA256',
                      encoded_signature.decode('utf-8')))
        if 'X-Amzn-Authorization' in request.headers:
            del request.headers['X-Amzn-Authorization']
        request.headers['X-Amzn-Authorization'] = signature


class SigV4Auth(BaseSigner):
    """
    Sign a request with Signature V4.
    """
    REQUIRES_REGION = True

    def __init__(self, credentials, service_name, region_name):
        self.credentials = credentials
        # We initialize these value here so the unit tests can have
        # valid values.  But these will get overriden in ``add_auth``
        # later for real requests.
        self._region_name = region_name
        self._service_name = service_name

    def _sign(self, key, msg, hex=False):
        if hex:
            sig = hmac.new(key, msg.encode('utf-8'), sha256).hexdigest()
        else:
            sig = hmac.new(key, msg.encode('utf-8'), sha256).digest()
        return sig

    def headers_to_sign(self, request):
        """
        Select the headers from the request that need to be included
        in the StringToSign.
        """
        header_map = HTTPHeaders()
        for name, value in request.headers.items():
            lname = name.lower()
            if lname not in SIGNED_HEADERS_BLACKLIST:
                header_map[lname] = value
        if 'host' not in header_map:
            # TODO: We should set the host ourselves, instead of relying on our
            # HTTP client to set it for us.
            header_map['host'] = _host_from_url(request.url)
        return header_map

    def canonical_query_string(self, request):
        # The query string can come from two parts.  One is the
        # params attribute of the request.  The other is from the request
        # url (in which case we have to re-split the url into its components
        # and parse out the query string component).
        if request.params:
            return self._canonical_query_string_params(request.params)
        else:
            return self._canonical_query_string_url(urlsplit(request.url))

    def _canonical_query_string_params(self, params):
        # [(key, value), (key2, value2)]
        key_val_pairs = []
        for key in params:
            value = str(params[key])
            key_val_pairs.append((quote(key, safe='-_.~'),
                                  quote(value, safe='-_.~')))
        sorted_key_vals = []
        # Sort by the URI-encoded key names, and in the case of
        # repeated keys, then sort by the value.
        for key, value in sorted(key_val_pairs):
            sorted_key_vals.append('%s=%s' % (key, value))
        canonical_query_string = '&'.join(sorted_key_vals)
        return canonical_query_string

    def _canonical_query_string_url(self, parts):
        canonical_query_string = ''
        if parts.query:
            # [(key, value), (key2, value2)]
            key_val_pairs = []
            for pair in parts.query.split('&'):
                key, _, value = pair.partition('=')
                key_val_pairs.append((key, value))
            sorted_key_vals = []
            # Sort by the URI-encoded key names, and in the case of
            # repeated keys, then sort by the value.
            for key, value in sorted(key_val_pairs):
                sorted_key_vals.append('%s=%s' % (key, value))
            canonical_query_string = '&'.join(sorted_key_vals)
        return canonical_query_string

    def canonical_headers(self, headers_to_sign):
        """
        Return the headers that need to be included in the StringToSign
        in their canonical form by converting all header keys to lower
        case, sorting them in alphabetical order and then joining
        them into a string, separated by newlines.
        """
        headers = []
        sorted_header_names = sorted(set(headers_to_sign))
        for key in sorted_header_names:
            value = ','.join(self._header_value(v) for v in
                             headers_to_sign.get_all(key))
            headers.append('%s:%s' % (key, ensure_unicode(value)))
        return '\n'.join(headers)

    def _header_value(self, value):
        # From the sigv4 docs:
        # Lowercase(HeaderName) + ':' + Trimall(HeaderValue)
        #
        # The Trimall function removes excess white space before and after
        # values, and converts sequential spaces to a single space.
        return ' '.join(value.split())

    def signed_headers(self, headers_to_sign):
        l = ['%s' % n.lower().strip() for n in set(headers_to_sign)]
        l = sorted(l)
        return ';'.join(l)

    def _is_streaming_checksum_payload(self, request):
        checksum_context = request.context.get('checksum', {})
        algorithm = checksum_context.get('request_algorithm')
        return isinstance(algorithm, dict) and algorithm.get('in') == 'trailer'

    def payload(self, request):
        if self._is_streaming_checksum_payload(request):
            return STREAMING_UNSIGNED_PAYLOAD_TRAILER
        elif not self._should_sha256_sign_payload(request):
            # When payload signing is disabled, we use this static string in
            # place of the payload checksum.
            return UNSIGNED_PAYLOAD
        request_body = request.body
        if request_body and hasattr(request_body, 'seek'):
            position = request_body.tell()
            read_chunksize = functools.partial(request_body.read,
                                               PAYLOAD_BUFFER)
            checksum = sha256()
            for chunk in iter(read_chunksize, b''):
                checksum.update(chunk)
            hex_checksum = checksum.hexdigest()
            request_body.seek(position)
            return hex_checksum
        elif request_body:
            # The request serialization has ensured that
            # request.body is a bytes() type.
            return sha256(request_body).hexdigest()
        else:
            return EMPTY_SHA256_HASH

    def _should_sha256_sign_payload(self, request):
        # Payloads will always be signed over insecure connections.
        if not request.url.startswith('https'):
            return True

        # Certain operations may have payload signing disabled by default.
        # Since we don't have access to the operation model, we pass in this
        # bit of metadata through the request context.
        return request.context.get('payload_signing_enabled', True)

    def canonical_request(self, request):
        cr = [request.method.upper()]
        path = self._normalize_url_path(urlsplit(request.url).path)
        cr.append(path)
        cr.append(self.canonical_query_string(request))
        headers_to_sign = self.headers_to_sign(request)
        cr.append(self.canonical_headers(headers_to_sign) + '\n')
        cr.append(self.signed_headers(headers_to_sign))
        if 'X-Amz-Content-SHA256' in request.headers:
            body_checksum = request.headers['X-Amz-Content-SHA256']
        else:
            body_checksum = self.payload(request)
        cr.append(body_checksum)
        return '\n'.join(cr)

    def _normalize_url_path(self, path):
        normalized_path = quote(normalize_url_path(path), safe='/~')
        return normalized_path

    def scope(self, request):
        scope = [self.credentials.access_key]
        scope.append(request.context['timestamp'][0:8])
        scope.append(self._region_name)
        scope.append(self._service_name)
        scope.append('aws4_request')
        return '/'.join(scope)

    def credential_scope(self, request):
        scope = []
        scope.append(request.context['timestamp'][0:8])
        scope.append(self._region_name)
        scope.append(self._service_name)
        scope.append('aws4_request')
        return '/'.join(scope)

    def string_to_sign(self, request, canonical_request):
        """
        Return the canonical StringToSign as well as a dict
        containing the original version of all headers that
        were included in the StringToSign.
        """
        sts = ['AWS4-HMAC-SHA256']
        sts.append(request.context['timestamp'])
        sts.append(self.credential_scope(request))
        sts.append(sha256(canonical_request.encode('utf-8')).hexdigest())
        return '\n'.join(sts)

    def signature(self, string_to_sign, request):
        key = self.credentials.secret_key
        k_date = self._sign(('AWS4' + key).encode('utf-8'),
                            request.context['timestamp'][0:8])
        k_region = self._sign(k_date, self._region_name)
        k_service = self._sign(k_region, self._service_name)
        k_signing = self._sign(k_service, 'aws4_request')
        return self._sign(k_signing, string_to_sign, hex=True)

    def add_auth(self, request):
        if self.credentials is None:
            raise NoCredentialsError()
        datetime_now = datetime.datetime.utcnow()
        request.context['timestamp'] = datetime_now.strftime(SIGV4_TIMESTAMP)
        # This could be a retry.  Make sure the previous
        # authorization header is removed first.
        self._modify_request_before_signing(request)
        canonical_request = self.canonical_request(request)
        logger.debug("Calculating signature using v4 auth.")
        logger.debug('CanonicalRequest:\n%s', canonical_request)
        string_to_sign = self.string_to_sign(request, canonical_request)
        logger.debug('StringToSign:\n%s', string_to_sign)
        signature = self.signature(string_to_sign, request)
        logger.debug('Signature:\n%s', signature)

        self._inject_signature_to_request(request, signature)

    def _inject_signature_to_request(self, request, signature):
        l = ['AWS4-HMAC-SHA256 Credential=%s' % self.scope(request)]
        headers_to_sign = self.headers_to_sign(request)
        l.append('SignedHeaders=%s' % self.signed_headers(headers_to_sign))
        l.append('Signature=%s' % signature)
        request.headers['Authorization'] = ', '.join(l)
        return request

    def _modify_request_before_signing(self, request):
        if 'Authorization' in request.headers:
            del request.headers['Authorization']
        self._set_necessary_date_headers(request)
        if self.credentials.token:
            if 'X-Amz-Security-Token' in request.headers:
                del request.headers['X-Amz-Security-Token']
            request.headers['X-Amz-Security-Token'] = self.credentials.token

        if not request.context.get('payload_signing_enabled', True):
            if 'X-Amz-Content-SHA256' in request.headers:
                del request.headers['X-Amz-Content-SHA256']
            request.headers['X-Amz-Content-SHA256'] = UNSIGNED_PAYLOAD

    def _set_necessary_date_headers(self, request):
        # The spec allows for either the Date _or_ the X-Amz-Date value to be
        # used so we check both.  If there's a Date header, we use the date
        # header.  Otherwise we use the X-Amz-Date header.
        if 'Date' in request.headers:
            del request.headers['Date']
            datetime_timestamp = datetime.datetime.strptime(
                request.context['timestamp'], SIGV4_TIMESTAMP)
            request.headers['Date'] = formatdate(
                int(calendar.timegm(datetime_timestamp.timetuple())))
            if 'X-Amz-Date' in request.headers:
                del request.headers['X-Amz-Date']
        else:
            if 'X-Amz-Date' in request.headers:
                del request.headers['X-Amz-Date']
            request.headers['X-Amz-Date'] = request.context['timestamp']


class S3SigV4Auth(SigV4Auth):
    def _modify_request_before_signing(self, request):
        super(S3SigV4Auth, self)._modify_request_before_signing(request)
        if 'X-Amz-Content-SHA256' in request.headers:
            del request.headers['X-Amz-Content-SHA256']

        request.headers['X-Amz-Content-SHA256'] = self.payload(request)

    def _should_sha256_sign_payload(self, request):
        # S3 allows optional body signing, so to minimize the performance
        # impact, we opt to not SHA256 sign the body on streaming uploads,
        # provided that we're on https.
        client_config = request.context.get('client_config')
        s3_config = getattr(client_config, 's3', None)

        # The config could be None if it isn't set, or if the customer sets it
        # to None.
        if s3_config is None:
            s3_config = {}

        # The explicit configuration takes precedence over any implicit
        # configuration.
        sign_payload = s3_config.get('payload_signing_enabled', None)
        if sign_payload is not None:
            return sign_payload

        # We require that both a checksum be present and https be enabled
        # to implicitly disable body signing. The combination of TLS and
        # a checksum is sufficiently secure and durable for us to be
        # confident in the request without body signing.
        checksum_header = 'Content-MD5'
        checksum_context = request.context.get('checksum', {})
        algorithm = checksum_context.get('request_algorithm')
        if isinstance(algorithm, dict) and algorithm.get('in') == 'header':
            checksum_header = algorithm['name']
        if not request.url.startswith('https') or \
                checksum_header not in request.headers:
            return True

        # If the input is streaming we disable body signing by default.
        if request.context.get('has_streaming_input', False):
            return False

        # If the S3-specific checks had no results, delegate to the generic
        # checks.
        return super(S3SigV4Auth, self)._should_sha256_sign_payload(request)

    def _normalize_url_path(self, path):
        # For S3, we do not normalize the path.
        return path


class S3ExpressAuth(S3SigV4Auth):
    REQUIRES_IDENTITY_CACHE = True

    def __init__(
        self, credentials, service_name, region_name, *, identity_cache
    ):
        super().__init__(credentials, service_name, region_name)
        self._identity_cache = identity_cache

    def add_auth(self, request):
        super().add_auth(request)

    def _modify_request_before_signing(self, request):
        super()._modify_request_before_signing(request)
        if 'x-amz-s3session-token' not in request.headers:
            request.headers['x-amz-s3session-token'] = self.credentials.token
        # S3Express does not support STS' X-Amz-Security-Token
        if 'X-Amz-Security-Token' in request.headers:
            del request.headers['X-Amz-Security-Token']


class S3ExpressPostAuth(S3ExpressAuth):
    REQUIRES_IDENTITY_CACHE = True

    def add_auth(self, request):
        datetime_now = datetime.datetime.utcnow()
        request.context['timestamp'] = datetime_now.strftime(SIGV4_TIMESTAMP)

        fields = {}
        if request.context.get('s3-presign-post-fields', None) is not None:
            fields = request.context['s3-presign-post-fields']

        policy = {}
        conditions = []
        if request.context.get('s3-presign-post-policy', None) is not None:
            policy = request.context['s3-presign-post-policy']
            if policy.get('conditions', None) is not None:
                conditions = policy['conditions']

        policy['conditions'] = conditions

        fields['x-amz-algorithm'] = 'AWS4-HMAC-SHA256'
        fields['x-amz-credential'] = self.scope(request)
        fields['x-amz-date'] = request.context['timestamp']

        conditions.append({'x-amz-algorithm': 'AWS4-HMAC-SHA256'})
        conditions.append({'x-amz-credential': self.scope(request)})
        conditions.append({'x-amz-date': request.context['timestamp']})

        if self.credentials.token is not None:
            fields['X-Amz-S3session-Token'] = self.credentials.token
            conditions.append(
                {'X-Amz-S3session-Token': self.credentials.token}
            )

        # Dump the base64 encoded policy into the fields dictionary.
        fields['policy'] = base64.b64encode(
            json.dumps(policy).encode('utf-8')
        ).decode('utf-8')

        fields['x-amz-signature'] = self.signature(fields['policy'], request)

        request.context['s3-presign-post-fields'] = fields
        request.context['s3-presign-post-policy'] = policy


class S3ExpressQueryAuth(S3ExpressAuth):
    DEFAULT_EXPIRES = 300
    REQUIRES_IDENTITY_CACHE = True

    def __init__(
        self,
        credentials,
        service_name,
        region_name,
        *,
        identity_cache,
        expires=DEFAULT_EXPIRES,
    ):
        super().__init__(
            credentials,
            service_name,
            region_name,
            identity_cache=identity_cache,
        )
        self._expires = expires

    def _modify_request_before_signing(self, request):
        # We automatically set this header, so if it's the auto-set value we
        # want to get rid of it since it doesn't make sense for presigned urls.
        content_type = request.headers.get('content-type')
        blocklisted_content_type = (
            'application/x-www-form-urlencoded; charset=utf-8'
        )
        if content_type == blocklisted_content_type:
            del request.headers['content-type']

        # Note that we're not including X-Amz-Signature.
        # From the docs: "The Canonical Query String must include all the query
        # parameters from the preceding table except for X-Amz-Signature.
        signed_headers = self.signed_headers(self.headers_to_sign(request))

        auth_params = {
            'X-Amz-Algorithm': 'AWS4-HMAC-SHA256',
            'X-Amz-Credential': self.scope(request),
            'X-Amz-Date': request.context['timestamp'],
            'X-Amz-Expires': self._expires,
            'X-Amz-SignedHeaders': signed_headers,
        }
        if self.credentials.token is not None:
            auth_params['X-Amz-S3session-Token'] = self.credentials.token
        # Now parse the original query string to a dict, inject our new query
        # params, and serialize back to a query string.
        url_parts = urlsplit(request.url)
        # parse_qs makes each value a list, but in our case we know we won't
        # have repeated keys so we know we have single element lists which we
        # can convert back to scalar values.
        query_string_parts = parse_qs(url_parts.query, keep_blank_values=True)
        query_dict = {k: v[0] for k, v in query_string_parts.items()}

        if request.params:
            query_dict.update(request.params)
            request.params = {}
        # The spec is particular about this.  It *has* to be:
        # https://<endpoint>?<operation params>&<auth params>
        # You can't mix the two types of params together, i.e just keep doing
        # new_query_params.update(op_params)
        # new_query_params.update(auth_params)
        # percent_encode_sequence(new_query_params)
        operation_params = ''
        if request.data:
            # We also need to move the body params into the query string. To
            # do this, we first have to convert it to a dict.
            query_dict.update(_get_body_as_dict(request))
            request.data = ''
        if query_dict:
            operation_params = percent_encode_sequence(query_dict) + '&'
        new_query_string = (
            f"{operation_params}{percent_encode_sequence(auth_params)}"
        )
        # url_parts is a tuple (and therefore immutable) so we need to create
        # a new url_parts with the new query string.
        # <part>   - <index>
        # scheme   - 0
        # netloc   - 1
        # path     - 2
        # query    - 3  <-- we're replacing this.
        # fragment - 4
        p = url_parts
        new_url_parts = (p[0], p[1], p[2], new_query_string, p[4])
        request.url = urlunsplit(new_url_parts)

    def _inject_signature_to_request(self, request, signature):
        # Rather than calculating an "Authorization" header, for the query
        # param quth, we just append an 'X-Amz-Signature' param to the end
        # of the query string.
        request.url += '&X-Amz-Signature=%s' % signature

    def _normalize_url_path(self, path):
        # For S3, we do not normalize the path.
        return path

    def payload(self, request):
        # From the doc link above:
        # "You don't include a payload hash in the Canonical Request, because
        # when you create a presigned URL, you don't know anything about the
        # payload. Instead, you use a constant string "UNSIGNED-PAYLOAD".
        return UNSIGNED_PAYLOAD


class SigV4QueryAuth(SigV4Auth):
    DEFAULT_EXPIRES = 3600

    def __init__(self, credentials, service_name, region_name,
                 expires=DEFAULT_EXPIRES):
        super(SigV4QueryAuth, self).__init__(credentials, service_name,
                                             region_name)
        self._expires = expires

    def _modify_request_before_signing(self, request):
        # We automatically set this header, so if it's the auto-set value we
        # want to get rid of it since it doesn't make sense for presigned urls.
        content_type = request.headers.get('content-type')
        blacklisted_content_type = (
            'application/x-www-form-urlencoded; charset=utf-8'
        )
        if content_type == blacklisted_content_type:
            del request.headers['content-type']

        # Note that we're not including X-Amz-Signature.
        # From the docs: "The Canonical Query String must include all the query
        # parameters from the preceding table except for X-Amz-Signature.
        signed_headers = self.signed_headers(self.headers_to_sign(request))

        auth_params = {
            'X-Amz-Algorithm': 'AWS4-HMAC-SHA256',
            'X-Amz-Credential': self.scope(request),
            'X-Amz-Date': request.context['timestamp'],
            'X-Amz-Expires': self._expires,
            'X-Amz-SignedHeaders': signed_headers,
        }
        if self.credentials.token is not None:
            auth_params['X-Amz-Security-Token'] = self.credentials.token
        # Now parse the original query string to a dict, inject our new query
        # params, and serialize back to a query string.
        url_parts = urlsplit(request.url)
        # parse_qs makes each value a list, but in our case we know we won't
        # have repeated keys so we know we have single element lists which we
        # can convert back to scalar values.
        query_dict = dict(
            [(k, v[0]) for k, v in
             parse_qs(url_parts.query, keep_blank_values=True).items()])
        # The spec is particular about this.  It *has* to be:
        # https://<endpoint>?<operation params>&<auth params>
        # You can't mix the two types of params together, i.e just keep doing
        # new_query_params.update(op_params)
        # new_query_params.update(auth_params)
        # percent_encode_sequence(new_query_params)
        operation_params = ''
        if request.data:
            # We also need to move the body params into the query string. To
            # do this, we first have to convert it to a dict.
            query_dict.update(_get_body_as_dict(request))
            request.data = ''
        if query_dict:
            operation_params = percent_encode_sequence(query_dict) + '&'
        new_query_string = (operation_params +
                            percent_encode_sequence(auth_params))
        # url_parts is a tuple (and therefore immutable) so we need to create
        # a new url_parts with the new query string.
        # <part>   - <index>
        # scheme   - 0
        # netloc   - 1
        # path     - 2
        # query    - 3  <-- we're replacing this.
        # fragment - 4
        p = url_parts
        new_url_parts = (p[0], p[1], p[2], new_query_string, p[4])
        request.url = urlunsplit(new_url_parts)

    def _inject_signature_to_request(self, request, signature):
        # Rather than calculating an "Authorization" header, for the query
        # param quth, we just append an 'X-Amz-Signature' param to the end
        # of the query string.
        request.url += '&X-Amz-Signature=%s' % signature


class S3SigV4QueryAuth(SigV4QueryAuth):
    """S3 SigV4 auth using query parameters.

    This signer will sign a request using query parameters and signature
    version 4, i.e a "presigned url" signer.

    Based off of:

    http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-query-string-auth.html

    """
    def _normalize_url_path(self, path):
        # For S3, we do not normalize the path.
        return path

    def payload(self, request):
        # From the doc link above:
        # "You don't include a payload hash in the Canonical Request, because
        # when you create a presigned URL, you don't know anything about the
        # payload. Instead, you use a constant string "UNSIGNED-PAYLOAD".
        return UNSIGNED_PAYLOAD


class S3SigV4PostAuth(SigV4Auth):
    """
    Presigns a s3 post

    Implementation doc here:
    http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-UsingHTTPPOST.html
    """
    def add_auth(self, request):
        datetime_now = datetime.datetime.utcnow()
        request.context['timestamp'] = datetime_now.strftime(SIGV4_TIMESTAMP)

        fields = {}
        if request.context.get('s3-presign-post-fields', None) is not None:
            fields = request.context['s3-presign-post-fields']

        policy = {}
        conditions = []
        if request.context.get('s3-presign-post-policy', None) is not None:
            policy = request.context['s3-presign-post-policy']
            if policy.get('conditions', None) is not None:
                conditions = policy['conditions']

        policy['conditions'] = conditions

        fields['x-amz-algorithm'] = 'AWS4-HMAC-SHA256'
        fields['x-amz-credential'] = self.scope(request)
        fields['x-amz-date'] = request.context['timestamp']

        conditions.append({'x-amz-algorithm': 'AWS4-HMAC-SHA256'})
        conditions.append({'x-amz-credential': self.scope(request)})
        conditions.append({'x-amz-date': request.context['timestamp']})

        if self.credentials.token is not None:
            fields['x-amz-security-token'] = self.credentials.token
            conditions.append({'x-amz-security-token': self.credentials.token})

        # Dump the base64 encoded policy into the fields dictionary.
        fields['policy'] = base64.b64encode(
            json.dumps(policy).encode('utf-8')).decode('utf-8')

        fields['x-amz-signature'] = self.signature(fields['policy'], request)

        request.context['s3-presign-post-fields'] = fields
        request.context['s3-presign-post-policy'] = policy


class BearerAuth(TokenSigner):
    """
    Performs bearer token authorization by placing the bearer token in the
    Authorization header as specified by Section 2.1 of RFC 6750.

    https://datatracker.ietf.org/doc/html/rfc6750#section-2.1
    """

    def add_auth(self, request):
        if self.auth_token is None:
            raise NoAuthTokenError()

        auth_header = f'Bearer {self.auth_token.token}'
        if 'Authorization' in request.headers:
            del request.headers['Authorization']
        request.headers['Authorization'] = auth_header


# NOTE: This import is at the bottom because it resolves an import error when
# the botocore.crt.auth module imports functions/classes defined above from
# this module. In the future, we should isolate those functions/classes into
# a separate utility module to avoid any potential circular import.
import botocore.crt.auth

def resolve_auth_type(auth_trait):
    for auth_type in auth_trait:
        if auth_type == 'smithy.api#noAuth':
            return AUTH_TYPE_TO_SIGNATURE_VERSION[auth_type]
        elif auth_type in AUTH_TYPE_TO_SIGNATURE_VERSION:
            signature_version = AUTH_TYPE_TO_SIGNATURE_VERSION[auth_type]
            if signature_version in AUTH_TYPE_MAPS:
                return signature_version
        else:
            raise UnknownSignatureVersionError(signature_version=auth_type)
    raise UnsupportedSignatureVersionError(signature_version=auth_trait)


# Defined at the bottom instead of the top of the module because the Auth
# classes weren't defined yet.
AUTH_TYPE_MAPS = {
    'v2': SigV2Auth,
    'v4': SigV4Auth,
    'v4a': botocore.crt.auth.CrtSigV4AsymAuth,
    'v4-query': SigV4QueryAuth,
    'v3': SigV3Auth,
    'v3https': SigV3Auth,
    's3v4': S3SigV4Auth,
    's3v4-query': S3SigV4QueryAuth,
    's3v4-presign-post': S3SigV4PostAuth,
    's3v4a': botocore.crt.auth.CrtS3SigV4AsymAuth,
    's3v4a-query': botocore.crt.auth.CrtS3SigV4AsymQueryAuth,
    'v4-s3express': S3ExpressAuth,
    'v4-s3express-query': S3ExpressQueryAuth,
    'v4-s3express-presign-post': S3ExpressPostAuth,
    'bearer': BearerAuth,
}

AUTH_TYPE_TO_SIGNATURE_VERSION = {
    'aws.auth#sigv4': 'v4',
    'aws.auth#sigv4a': 'v4a',
    'smithy.api#httpBearerAuth': 'bearer',
    'smithy.api#noAuth': 'none',
}