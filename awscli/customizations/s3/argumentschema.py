from awscli.customizations.s3.utils import AppendFilter

RECURSIVE = {
    'name': 'recursive',
    'action': 'store_true',
    'dest': 'dir_op',
    'help_text': (
        "Command is performed on all files or objects "
        "under the specified directory or prefix."
    ),
}


HUMAN_READABLE = {
    'name': 'human-readable',
    'action': 'store_true',
    'help_text': "Displays file sizes in human readable format.",
}


SUMMARIZE = {
    'name': 'summarize',
    'action': 'store_true',
    'help_text': (
        "Displays summary information (number of objects, total size)."
    ),
}


DRYRUN = {
    'name': 'dryrun',
    'action': 'store_true',
    'help_text': (
        "Displays the operations that would be performed using the "
        "specified command without actually running them."
    ),
}


QUIET = {
    'name': 'quiet',
    'action': 'store_true',
    'help_text': (
        "Does not display the operations performed from the specified command."
    ),
}


FORCE = {
    'name': 'force',
    'action': 'store_true',
    'help_text': (
        "Deletes all objects in the bucket including the bucket itself. "
        "Note that versioned objects will not be deleted in this "
        "process which would cause the bucket deletion to fail because "
        "the bucket would not be empty. To delete versioned "
        "objects use the ``s3api delete-object`` command with "
        "the ``--version-id`` parameter."
    ),
}


FOLLOW_SYMLINKS = {
    'name': 'follow-symlinks',
    'action': 'store_true',
    'default': True,
    'group_name': 'follow_symlinks',
    'help_text': (
        "Symbolic links are followed "
        "only when uploading to S3 from the local filesystem. "
        "Note that S3 does not support symbolic links, so the "
        "contents of the link target are uploaded under the "
        "name of the link. When neither ``--follow-symlinks`` "
        "nor ``--no-follow-symlinks`` is specified, the default "
        "is to follow symlinks."
    ),
}


NO_FOLLOW_SYMLINKS = {
    'name': 'no-follow-symlinks',
    'action': 'store_false',
    'dest': 'follow_symlinks',
    'default': True,
    'group_name': 'follow_symlinks',
}


NO_GUESS_MIME_TYPE = {
    'name': 'no-guess-mime-type',
    'action': 'store_false',
    'dest': 'guess_mime_type',
    'default': True,
    'help_text': (
        "Do not try to guess the mime type for "
        "uploaded files.  By default the mime type of a "
        "file is guessed when it is uploaded."
    ),
}


CONTENT_TYPE = {
    'name': 'content-type',
    'help_text': (
        "Specify an explicit content type for this operation.  "
        "This value overrides any guessed mime types."
    ),
}


EXCLUDE = {
    'name': 'exclude',
    'action': AppendFilter,
    'nargs': 1,
    'dest': 'filters',
    'help_text': (
        "Exclude all files or objects from the command that matches "
        "the specified pattern."
    ),
}


INCLUDE = {
    'name': 'include',
    'action': AppendFilter,
    'nargs': 1,
    'dest': 'filters',
    'help_text': (
        "Don't exclude files or objects "
        "in the command that match the specified pattern. "
        'See <a href="http://docs.aws.amazon.com/cli/latest/reference'
        '/s3/index.html#use-of-exclude-and-include-filters">Use of '
        'Exclude and Include Filters</a> for details.'
    ),
}


ACL = {
    'name': 'acl',
    'choices': [
        'private',
        'public-read',
        'public-read-write',
        'authenticated-read',
        'aws-exec-read',
        'bucket-owner-read',
        'bucket-owner-full-control',
        'log-delivery-write',
    ],
    'help_text': (
        "Sets the ACL for the object when the command is "
        "performed.  If you use this parameter you must have the "
        '"s3:PutObjectAcl" permission included in the list of actions '
        "for your IAM policy. "
        "Only accepts values of ``private``, ``public-read``, "
        "``public-read-write``, ``authenticated-read``, ``aws-exec-read``, "
        "``bucket-owner-read``, ``bucket-owner-full-control`` and "
        "``log-delivery-write``. "
        'See <a href="http://docs.aws.amazon.com/AmazonS3/latest/dev/'
        'acl-overview.html#canned-acl">Canned ACL</a> for details'
    ),
}


GRANTS = {
    'name': 'grants',
    'nargs': '+',
    'help_text': (
        '<p>Grant specific permissions to individual users or groups. You '
        'can supply a list of grants of the form</p><codeblock>--grants '
        'Permission=Grantee_Type=Grantee_ID [Permission=Grantee_Type='
        'Grantee_ID ...]</codeblock>To specify the same permission type '
        'for multiple '
        'grantees, specify the permission as such as <codeblock>--grants '
        'Permission=Grantee_Type=Grantee_ID,Grantee_Type=Grantee_ID,...'
        '</codeblock>Each value contains the following elements:'
        '<ul><li><code>Permission</code> - Specifies '
        'the granted permissions, and can be set to read, readacl, '
        'writeacl, or full.</li><li><code>Grantee_Type</code> - '
        'Specifies how the grantee is to be identified, and can be set '
        'to uri or id.</li><li><code>Grantee_ID</code> - '
        'Specifies the grantee based on Grantee_Type. The '
        '<code>Grantee_ID</code> value can be one of:<ul><li><b>uri</b> '
        '- The group\'s URI. For more information, see '
        '<a href="http://docs.aws.amazon.com/AmazonS3/latest/dev/'
        'ACLOverview.html#SpecifyingGrantee">'
        'Who Is a Grantee?</a></li>'
        '<li><b>id</b> - The account\'s canonical ID</li></ul>'
        '</li></ul>'
        'For more information on Amazon S3 access control, see '
        '<a href="http://docs.aws.amazon.com/AmazonS3/latest/dev/'
        'UsingAuthAccess.html">Access Control</a>'
    ),
}


SSE = {
    'name': 'sse',
    'nargs': '?',
    'const': 'AES256',
    'choices': ['AES256', 'aws:kms'],
    'help_text': (
        'Specifies server-side encryption of the object in S3. '
        'Valid values are ``AES256`` and ``aws:kms``. If the parameter is '
        'specified but no value is provided, ``AES256`` is used.'
    ),
}


SSE_C = {
    'name': 'sse-c',
    'nargs': '?',
    'const': 'AES256',
    'choices': ['AES256'],
    'help_text': (
        'Specifies server-side encryption using customer provided keys '
        'of the the object in S3. ``AES256`` is the only valid value. '
        'If the parameter is specified but no value is provided, '
        '``AES256`` is used. If you provide this value, ``--sse-c-key`` '
        'must be specified as well.'
    ),
}


SSE_C_KEY = {
    'name': 'sse-c-key',
    'cli_type_name': 'blob',
    'help_text': (
        'The customer-provided encryption key to use to server-side '
        'encrypt the object in S3. If you provide this value, '
        '``--sse-c`` must be specified as well. The key provided should '
        '**not** be base64 encoded.'
    ),
}


SSE_KMS_KEY_ID = {
    'name': 'sse-kms-key-id',
    'help_text': (
        'The customer-managed AWS Key Management Service (KMS) key ID that '
        'should be used to server-side encrypt the object in S3. You should '
        'only provide this parameter if you are using a customer managed '
        'customer master key (CMK) and not the AWS managed KMS CMK.'
    ),
}


SSE_C_COPY_SOURCE = {
    'name': 'sse-c-copy-source',
    'nargs': '?',
    'const': 'AES256',
    'choices': ['AES256'],
    'help_text': (
        'This parameter should only be specified when copying an S3 object '
        'that was encrypted server-side with a customer-provided '
        'key. It specifies the algorithm to use when decrypting the source '
        'object. ``AES256`` is the only valid '
        'value. If the parameter is specified but no value is provided, '
        '``AES256`` is used. If you provide this value, '
        '``--sse-c-copy-source-key`` must be specified as well. '
    ),
}


SSE_C_COPY_SOURCE_KEY = {
    'name': 'sse-c-copy-source-key',
    'cli_type_name': 'blob',
    'help_text': (
        'This parameter should only be specified when copying an S3 object '
        'that was encrypted server-side with a customer-provided '
        'key. Specifies the customer-provided encryption key for Amazon S3 '
        'to use to decrypt the source object. The encryption key provided '
        'must be one that was used when the source object was created. '
        'If you provide this value, ``--sse-c-copy-source`` be specified as '
        'well. The key provided should **not** be base64 encoded.'
    ),
}


STORAGE_CLASS = {
    'name': 'storage-class',
    'choices': [
        'STANDARD',
        'REDUCED_REDUNDANCY',
        'STANDARD_IA',
        'ONEZONE_IA',
        'INTELLIGENT_TIERING',
        'GLACIER',
        'DEEP_ARCHIVE',
        'GLACIER_IR',
    ],
    'help_text': (
        "The type of storage to use for the object. "
        "Valid choices are: STANDARD | REDUCED_REDUNDANCY "
        "| STANDARD_IA | ONEZONE_IA | INTELLIGENT_TIERING "
        "| GLACIER | DEEP_ARCHIVE | GLACIER_IR. "
        "Defaults to 'STANDARD'"
    ),
}


WEBSITE_REDIRECT = {
    'name': 'website-redirect',
    'help_text': (
        "If the bucket is configured as a website, "
        "redirects requests for this object to another object "
        "in the same bucket or to an external URL. Amazon S3 "
        "stores the value of this header in the object "
        "metadata."
    ),
}


CACHE_CONTROL = {
    'name': 'cache-control',
    'help_text': ("Specifies caching behavior along the request/reply chain."),
}


CONTENT_DISPOSITION = {
    'name': 'content-disposition',
    'help_text': ("Specifies presentational information for the object."),
}


CONTENT_ENCODING = {
    'name': 'content-encoding',
    'help_text': (
        "Specifies what content encodings have been "
        "applied to the object and thus what decoding "
        "mechanisms must be applied to obtain the media-type "
        "referenced by the Content-Type header field."
    ),
}


CONTENT_LANGUAGE = {
    'name': 'content-language',
    'help_text': ("The language the content is in."),
}


SOURCE_REGION = {
    'name': 'source-region',
    'help_text': (
        "When transferring objects from an s3 bucket to an s3 "
        "bucket, this specifies the region of the source bucket."
        " Note the region specified by ``--region`` or through "
        "configuration of the CLI refers to the region of the "
        "destination bucket.  If ``--source-region`` is not "
        "specified the region of the source will be the same "
        "as the region of the destination bucket."
    ),
}


EXPIRES = {
    'name': 'expires',
    'help_text': (
        "The date and time at which the object is no longer cacheable."
    ),
}


METADATA = {
    'name': 'metadata',
    'cli_type_name': 'map',
    'schema': {
        'type': 'map',
        'key': {'type': 'string'},
        'value': {'type': 'string'},
    },
    'help_text': (
        "A map of metadata to store with the objects in S3. This will be "
        "applied to every object which is part of this request. In a sync, "
        "this means that files which haven't changed won't receive the new "
        "metadata. "
    ),
}


METADATA_DIRECTIVE = {
    'name': 'metadata-directive',
    'choices': ['COPY', 'REPLACE'],
    'help_text': (
        'Sets the ``x-amz-metadata-directive`` header for CopyObject '
        'operations. It is recommended to use the ``--copy-props`` parameter '
        'instead to control copying of metadata properties. '
        'If ``--metadata-directive`` is set, the ``--copy-props`` parameter '
        'will be disabled and will have no affect on the transfer.'
    ),
}


COPY_PROPS = {
    'name': 'copy-props',
    'choices': ['none', 'metadata-directive', 'default'],
    'default': 'default',
    'help_text': (
        'Determines which properties are copied from the source S3 object. '
        'This parameter only applies for S3 to S3 copies. Valid values are: '
        '<ul>'
        '<li>``none`` - Do not copy any of the properties from the source '
        'S3 object.</li>'
        '<li>``metadata-directive`` - Copies the following properties from '
        'the source S3 object: '
        '``content-type``, ``content-language``, ``content-encoding``, '
        '``content-disposition``, ``cache-control``, ``--expires``, and '
        '``metadata``</li>'
        '<li>``default`` - The default value. Copies tags and properties '
        'covered under the ``metadata-directive`` value from the '
        'source S3 object.</li>'
        '</ul>'
        'In order to copy the appropriate properties for multipart copies, '
        'some of the options may require additional API calls if a multipart '
        'copy is involved. Specifically:'
        '<ul>'
        '<li>``metadata-directive`` may require additional ``HeadObject`` '
        'API calls.</li>'
        '<li>``default`` may require additional ``HeadObject``, '
        '``GetObjectTagging``, and ``PutObjectTagging`` API calls. Note this'
        ' list of API calls may grow in the future in order to ensure '
        'multipart copies preserve the exact properties a ``CopyObject`` '
        'API call would preserve.</li>'
        '</ul>'
        'If you want to guarantee no additional API calls are made other than '
        'than the ones needed to perform the actual copy, set this option to '
        '``none``.'
    ),
}


INDEX_DOCUMENT = {
    'name': 'index-document',
    'help_text': (
        'A suffix that is appended to a request that is for '
        'a directory on the website endpoint (e.g. if the '
        'suffix is index.html and you make a request to '
        'samplebucket/images/ the data that is returned '
        'will be for the object with the key name '
        'images/index.html) The suffix must not be empty and '
        'must not include a slash character.'
    ),
}


ERROR_DOCUMENT = {
    'name': 'error-document',
    'help_text': ('The object key name to use when a 4XX class error occurs.'),
}


ONLY_SHOW_ERRORS = {
    'name': 'only-show-errors',
    'action': 'store_true',
    'help_text': (
        'Only errors and warnings are displayed. All other '
        'output is suppressed.'
    ),
}


NO_PROGRESS = {
    'name': 'no-progress',
    'action': 'store_false',
    'dest': 'progress',
    'help_text': (
        'File transfer progress is not displayed. This flag '
        'is only applied when the quiet and only-show-errors '
        'flags are not provided.'
    ),
}


EXPECTED_SIZE = {
    'name': 'expected-size',
    'help_text': (
        'This argument specifies the expected size of a stream '
        'in terms of bytes. Note that this argument is needed '
        'only when a stream is being uploaded to s3 and the size '
        'is larger than 50GB.  Failure to include this argument '
        'under these conditions may result in a failed upload '
        'due to too many parts in upload.'
    ),
}


PAGE_SIZE = {
    'name': 'page-size',
    'cli_type_name': 'integer',
    'help_text': (
        'The number of results to return in each response to a list '
        'operation. The default value is 1000 (the maximum allowed). '
        'Using a lower value may help if an operation times out.'
    ),
}


IGNORE_GLACIER_WARNINGS = {
    'name': 'ignore-glacier-warnings',
    'action': 'store_true',
    'help_text': (
        'Turns off glacier warnings. Warnings about an operation that cannot '
        'be performed because it involves copying, downloading, or moving '
        'a glacier object will no longer be printed to standard error and '
        'will no longer cause the return code of the command to be ``2``.'
    ),
}


FORCE_GLACIER_TRANSFER = {
    'name': 'force-glacier-transfer',
    'action': 'store_true',
    'help_text': (
        'Forces a transfer request on all Glacier objects in a sync or '
        'recursive copy.'
    ),
}

REQUEST_PAYER = {
    'name': 'request-payer',
    'choices': ['requester'],
    'nargs': '?',
    'const': 'requester',
    'help_text': (
        'Confirms that the requester knows that they will be charged '
        'for the request. Bucket owners need not specify this parameter in '
        'their requests. Documentation on downloading objects from requester '
        'pays buckets can be found at '
        'http://docs.aws.amazon.com/AmazonS3/latest/dev/'
        'ObjectsinRequesterPaysBuckets.html'
    ),
}

VALIDATE_SAME_S3_PATHS = {
    'name': 'validate-same-s3-paths',
    'action': 'store_true',
    'help_text': (
        'Resolves the source and destination S3 URIs to their '
        'underlying buckets and verifies that the file or object '
        'is not being moved onto itself. If you are using any type '
        'of access point ARNs or access point aliases in your S3 URIs, '
        'we strongly recommended using this parameter to help prevent '
        'accidental deletions of the source file or object. This '
        'parameter resolves the underlying buckets of S3 access point '
        'ARNs and aliases, S3 on Outposts access point ARNs, and '
        'Multi-Region Access Point ARNs. S3 on Outposts access point '
        'aliases are not supported. Instead of using this parameter, '
        'you can set the environment variable '
        '``AWS_CLI_S3_MV_VALIDATE_SAME_S3_PATHS`` to ``true``. '
        'NOTE: Path validation requires making additional API calls. '
        'Future updates to this path-validation mechanism might change '
        'which API calls are made.'
    ),
}

CHECKSUM_MODE = {
    'name': 'checksum-mode',
    'choices': ['ENABLED'],
    'help_text': 'To retrieve the checksum, this mode must be enabled. If the object has a '
    'checksum, it will be verified.',
}

CHECKSUM_ALGORITHM = {
    'name': 'checksum-algorithm',
    'choices': ['CRC64NVME', 'CRC32', 'SHA256', 'SHA1', 'CRC32C'],
    'help_text': 'Indicates the algorithm used to create the checksum for the object.',
}

BUCKET_NAME_PREFIX = {
    'name': 'bucket-name-prefix',
    'help_text': (
        'Limits the response to bucket names that begin with the specified '
        'bucket name prefix.'
    ),
}

BUCKET_REGION = {
    'name': 'bucket-region',
    'help_text': (
        'Limits the response to buckets that are located in the specified '
        'Amazon Web Services Region. The Amazon Web Services Region must be '
        'expressed according to the Amazon Web Services Region code, such as '
        'us-west-2 for the US West (Oregon) Region. For a list of the valid '
        'values for all of the Amazon Web Services Regions, see '
        'https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region'
    ),
}

NO_CLOBBER = {
    'name': 'no-clobber',
    'action': 'store_true',
    'help_text': (
        'Will not overwrite any file(s) in the destination. For cp or mv, '
        'this will result in an extra S3 GET or HEAD request.'
    ),
}

NO_CREATE = {
    'name': 'no-create',
    'action': 'store_true',
    'help_text': (
        'Will not create any new file(s) in the destination. For cp or mv, '
        'this will result in an extra S3 GET or HEAD request.'
    ),
}

# sync-specific args

DELETE = {
    'name': 'delete',
    'action': 'store_true',
    'help_text': (
        "Files that exist in the destination but not in the source are "
        "deleted during sync. Note that files excluded by filters are "
        "excluded from deletion."
    ),
}

EXACT_TIMESTAMPS = {
    'name': 'exact-timestamps',
    'action': 'store_true',
    'help_text': (
        'When syncing from S3 to local, same-sized '
        'items will be ignored only when the timestamps '
        'match exactly. The default behavior is to ignore '
        'same-sized items unless the local version is newer '
        'than the S3 version.'
    ),
}

SIZE_ONLY = {
    'name': 'size-only',
    'action': 'store_true',
    'help_text': (
        'Makes the size of each key the only criteria used to '
        'decide whether to sync from source to destination.'
    ),
}