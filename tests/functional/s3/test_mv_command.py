#!/usr/bin/env python
# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import os

from awscrt.s3 import S3RequestType

from awscli.compat import BytesIO
from awscli.customizations.s3.utils import S3PathResolver
from awscli.testutils import mock
from tests.functional.s3 import (
    BaseS3TransferCommandTest, BaseCRTTransferClientTest
)
from tests import requires_crt

class TestMvCommand(BaseS3TransferCommandTest):

    prefix = 's3 mv '

    def test_cant_mv_object_onto_itself(self):
        cmdline = '%s s3://bucket/key s3://bucket/key' % self.prefix
        stderr = self.run_cmd(cmdline, expected_rc=252)[1]
        self.assertIn('Cannot mv a file onto itself', stderr)

    def test_cant_mv_object_with_implied_name(self):
        # The "key" key name is implied in the dst argument.
        cmdline = '%s s3://bucket/key s3://bucket/' % self.prefix
        stderr = self.run_cmd(cmdline, expected_rc=252)[1]
        self.assertIn('Cannot mv a file onto itself', stderr)

    def test_dryrun_move(self):
        self.parsed_responses = [self.head_object_response()]
        cmdline = (
            f'{self.prefix} s3://bucket/key.txt s3://bucket/key2.txt --dryrun'
        )
        stdout, _, _ = self.run_cmd(cmdline, expected_rc=0)
        self.assert_operations_called(
            [
                ('HeadObject', {
                    'Bucket': 'bucket',
                    'Key': 'key.txt',
                })
            ]
        )
        self.assertIn(
            '(dryrun) move: s3://bucket/key.txt to s3://bucket/key2.txt',
            stdout
        )

    def test_website_redirect_ignore_paramfile(self):
        full_path = self.files.create_file('foo.txt', 'mycontent')
        cmdline = '%s %s s3://bucket/key.txt --website-redirect %s' % \
            (self.prefix, full_path, 'http://someserver')
        self.parsed_responses = [{'ETag': '"c8afdb36c52cf4727836669019e69222"'}]
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(self.operations_called[0][0].name, 'PutObject')
        # Make sure that the specified web address is used as opposed to the
        # contents of the web address.
        self.assertEqual(
            self.operations_called[0][1]['WebsiteRedirectLocation'],
            'http://someserver'
        )

    def test_metadata_directive_copy(self):
        self.parsed_responses = [
            {"ContentLength": "100", "LastModified": "00:00:00Z"},
            {'ETag': '"foo-1"'},
            {'ETag': '"foo-2"'}
        ]
        cmdline = ('%s s3://bucket/key.txt s3://bucket/key2.txt'
                   ' --metadata-directive REPLACE' % self.prefix)
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(len(self.operations_called), 3,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'HeadObject')
        self.assertEqual(self.operations_called[1][0].name, 'CopyObject')
        self.assertEqual(self.operations_called[2][0].name, 'DeleteObject')
        self.assertEqual(self.operations_called[1][1]['MetadataDirective'],
                         'REPLACE')

    def test_no_metadata_directive_for_non_copy(self):
        full_path = self.files.create_file('foo.txt', 'mycontent')
        cmdline = '%s %s s3://bucket --metadata-directive REPLACE' % \
            (self.prefix, full_path)
        self.parsed_responses = \
            [{'ETag': '"c8afdb36c52cf4727836669019e69222"'}]
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(len(self.operations_called), 1,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'PutObject')
        self.assertNotIn('MetadataDirective', self.operations_called[0][1])

    def test_download_move_with_request_payer(self):
        cmdline = '%s s3://mybucket/mykey %s --request-payer' % (
            self.prefix, self.files.rootdir)

        self.parsed_responses = [
            # Response for HeadObject
            {"ContentLength": 100, "LastModified": "00:00:00Z"},
            # Response for GetObject
            {'ETag': '"foo-1"', 'Body': BytesIO(b'foo')},
            # Response for DeleteObject
            {}
        ]

        self.run_cmd(cmdline, expected_rc=0)
        self.assert_operations_called(
            [
                ('HeadObject', {
                    'Bucket': 'mybucket',
                    'Key': 'mykey',
                    'RequestPayer': 'requester',
                }),
                ('GetObject', {
                    'Bucket': 'mybucket',
                    'Key': 'mykey',
                    'RequestPayer': 'requester',
                }),
                ('DeleteObject', {
                    'Bucket': 'mybucket',
                    'Key': 'mykey',
                    'RequestPayer': 'requester',
                })
            ]
        )

    def test_copy_move_with_request_payer(self):
        cmdline = self.prefix
        cmdline += 's3://sourcebucket/sourcekey s3://mybucket/mykey'
        cmdline += ' --request-payer'

        self.parsed_responses = [
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        self.run_cmd(cmdline, expected_rc=0)
        self.assert_operations_called(
            [
                self.head_object_request(
                    'sourcebucket', 'sourcekey', RequestPayer='requester'),
                self.copy_object_request(
                    'sourcebucket', 'sourcekey', 'mybucket', 'mykey',
                    RequestPayer='requester'),
                self.delete_object_request(
                    'sourcebucket', 'sourcekey', RequestPayer='requester')
            ]
        )

    def test_with_copy_props(self):
        cmdline = self.prefix
        cmdline += 's3://sourcebucket/sourcekey s3://bucket/key'
        cmdline += ' --copy-props default'

        upload_id = 'upload_id'
        large_tag_set = {'tag-key': 'val' * 3000}
        metadata = {'tag-key': 'tag-value'}
        self.parsed_responses = [
            self.head_object_response(
                Metadata=metadata,
                ContentLength=8 * 1024 ** 2
            ),
            self.get_object_tagging_response(large_tag_set),
            self.create_mpu_response(upload_id),
            self.upload_part_copy_response(),
            self.complete_mpu_response(),
            self.put_object_tagging_response(),
            self.delete_object_response()
        ]
        self.run_cmd(cmdline, expected_rc=0)
        self.assert_operations_called(
            [
                self.head_object_request('sourcebucket', 'sourcekey'),
                self.get_object_tagging_request('sourcebucket', 'sourcekey'),
                self.create_mpu_request('bucket', 'key', Metadata=metadata),
                self.upload_part_copy_request(
                    'sourcebucket', 'sourcekey', 'bucket', 'key', upload_id,
                    CopySourceRange=mock.ANY, PartNumber=1,
                ),
                self.complete_mpu_request('bucket', 'key', upload_id, 1),
                self.put_object_tagging_request(
                    'bucket', 'key', large_tag_set
                ),
                self.delete_object_request('sourcebucket', 'sourcekey')
            ]
        )

    def test_mv_does_not_delete_source_on_failed_put_tagging(self):
        cmdline = self.prefix
        cmdline += 's3://sourcebucket/sourcekey s3://bucket/key'
        cmdline += ' --copy-props default'

        upload_id = 'upload_id'
        large_tag_set = {'tag-key': 'val' * 3000}
        metadata = {'tag-key': 'tag-value'}
        self.parsed_responses = [
            self.head_object_response(
                Metadata=metadata,
                ContentLength=8 * 1024 ** 2
            ),
            self.get_object_tagging_response(large_tag_set),
            self.create_mpu_response(upload_id),
            self.upload_part_copy_response(),
            self.complete_mpu_response(),
            self.access_denied_error_response(),  # PutObjectTagging error
            self.delete_object_response(),
        ]
        self.set_http_status_codes(
            [
                200,  # HeadObject
                200,  # GetObjectTagging
                200,  # CreateMultipartUpload
                200,  # UploadPartCopy
                200,  # CompleteMultipartUpload
                403,  # PutObjectTagging
                200,  # DeleteObject
            ]
        )
        self.run_cmd(cmdline, expected_rc=1)
        self.assert_operations_called(
            [
                self.head_object_request('sourcebucket', 'sourcekey'),
                self.get_object_tagging_request('sourcebucket', 'sourcekey'),
                self.create_mpu_request('bucket', 'key', Metadata=metadata),
                self.upload_part_copy_request(
                    'sourcebucket', 'sourcekey', 'bucket', 'key', upload_id,
                    CopySourceRange=mock.ANY, PartNumber=1,
                ),
                self.complete_mpu_request('bucket', 'key', upload_id, 1),
                self.put_object_tagging_request(
                    'bucket', 'key', large_tag_set
                ),
                self.delete_object_request('bucket', 'key')
            ]
        )

    def test_upload_with_flexible_checksum_crc32(self):
        # TODO Ahmed
        pass

    def test_download_with_flexible_checksum_crc32(self):
        # TODO Ahmed
        pass


class TestMvWithCRTClient(BaseCRTTransferClientTest):
    def test_upload_move_using_crt_client(self):
        filename = self.files.create_file('myfile', 'mycontent')
        cmdline = [
            's3', 'mv', filename, 's3://bucket/key',
        ]
        self.run_command(cmdline)
        crt_requests = self.get_crt_make_request_calls()
        self.assertEqual(len(crt_requests), 1)
        self.assert_crt_make_request_call(
            crt_requests[0],
            expected_type=S3RequestType.PUT_OBJECT,
            expected_host=self.get_virtual_s3_host('bucket'),
            expected_path='/key',
            expected_send_filepath=filename,
        )
        self.assertFalse(os.path.exists(filename))

    def test_download_move_using_crt_client(self):
        filename = os.path.join(self.files.rootdir, 'myfile')
        cmdline = [
            's3', 'mv', 's3://bucket/key', filename
        ]
        self.add_botocore_head_object_response()
        self.add_botocore_delete_object_response()
        result = self.cli_runner.run(cmdline)
        self.assertEqual(result.rc, 0)
        crt_requests = self.get_crt_make_request_calls()
        self.assertEqual(len(crt_requests), 1)
        self.assert_crt_make_request_call(
            crt_requests[0],
            expected_type=S3RequestType.GET_OBJECT,
            expected_host=self.get_virtual_s3_host('bucket'),
            expected_path='/key',
            expected_recv_startswith=filename,
        )
        self.assert_no_remaining_botocore_responses()

    def test_does_not_use_crt_client_for_copy_moves(self):
        cmdline = [
            's3', 'mv', 's3://bucket/key', 's3://otherbucket/'
        ]
        self.add_botocore_head_object_response()
        self.add_botocore_copy_object_response()
        self.add_botocore_delete_object_response()
        self.run_command(cmdline)
        self.assertEqual(self.get_crt_make_request_calls(), [])
        self.assert_no_remaining_botocore_responses()

class TestMvCommandWithValidateSameS3Paths(BaseS3TransferCommandTest):

    prefix = 's3 mv '

    def assert_validates_cannot_mv_onto_itself(self, cmd):
        stderr = self.run_cmd(cmd, expected_rc=252)[1]
        self.assertIn('Cannot mv a file onto itself', stderr)

    def assert_runs_mv_without_validation(self, cmd):
        self.parsed_responses = [
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        self.run_cmd(cmd, expected_rc=0)
        self.assertEqual(len(self.operations_called), 3,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'HeadObject')
        self.assertEqual(self.operations_called[1][0].name, 'CopyObject')
        self.assertEqual(self.operations_called[2][0].name, 'DeleteObject')

    def assert_raises_warning(self, cmd):
        self.parsed_responses = [
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        stderr = self.run_cmd(cmd, expected_rc=0)[1]
        self.assertIn('warning: Provided s3 paths may resolve', stderr)

    def test_cant_mv_object_onto_itself_access_point_arn(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_cant_mv_object_onto_itself_access_point_arn_as_source(self):
        cmdline = (f"{self.prefix}s3://arn:aws:s3:us-west-2:123456789012:"
                   "accesspoint/myaccesspoint/key "
                   "s3://bucket/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_cant_mv_object_onto_itself_access_point_arn_with_env_var(self):
        self.environ['AWS_CLI_S3_MV_VALIDATE_SAME_S3_PATHS'] = 'true'
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/key")
        self.parsed_responses = [
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_cant_mv_object_onto_itself_access_point_arn_base_key(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/ "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_cant_mv_object_onto_itself_access_point_arn_base_prefix(self):
        cmdline = (f"{self.prefix}s3://bucket/prefix/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/prefix/ "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_cant_mv_object_onto_itself_access_point_alias(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://myaccesspoint-foobar-s3alias/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Account": "123456789012"},
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_cant_mv_object_onto_itself_outpost_access_point_arn(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3-outposts:us-east-1:123456789012:outpost/"
                   "op-foobar/accesspoint/myaccesspoint/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "bucket"}
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_outpost_access_point_alias_raises_error(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://myaccesspoint-foobar--op-s3/key "
                   "--validate-same-s3-paths")
        stderr = self.run_cmd(cmdline, expected_rc=252)[1]
        self.assertIn("Can't resolve underlying bucket name", stderr)

    def test_cant_mv_object_onto_itself_mrap_arn(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://arn:aws:s3::123456789012:accesspoint/foobar.mrap/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {
                "AccessPoints": [{
                    "Alias": "foobar.mrap",
                    "Regions": [
                        {"Bucket": "differentbucket"},
                        {"Bucket": "bucket"}
                    ]
                }]
            }
        ]
        self.assert_validates_cannot_mv_onto_itself(cmdline)

    def test_get_mrap_buckets_raises_if_alias_not_found(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://arn:aws:s3::123456789012:accesspoint/foobar.mrap/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {
                "AccessPoints": [{
                    "Alias": "baz.mrap",
                    "Regions": [
                        {"Bucket": "differentbucket"},
                        {"Bucket": "bucket"}
                    ]
                }]
            }
        ]
        stderr = self.run_cmd(cmdline, expected_rc=252)[1]
        self.assertEqual(
            "\nCouldn't find multi-region access point with alias foobar.mrap "
            "in account 123456789012\n",
            stderr
        )

    def test_mv_works_if_access_point_arn_resolves_to_different_bucket(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "differentbucket"},
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(len(self.operations_called), 4,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'GetAccessPoint')
        self.assertEqual(self.operations_called[1][0].name, 'HeadObject')
        self.assertEqual(self.operations_called[2][0].name, 'CopyObject')
        self.assertEqual(self.operations_called[3][0].name, 'DeleteObject')

    def test_mv_works_if_access_point_alias_resolves_to_different_bucket(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://myaccesspoint-foobar-s3alias/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Account": "123456789012"},
            {"Bucket": "differentbucket"},
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(len(self.operations_called), 5,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'GetCallerIdentity')
        self.assertEqual(self.operations_called[1][0].name, 'GetAccessPoint')
        self.assertEqual(self.operations_called[2][0].name, 'HeadObject')
        self.assertEqual(self.operations_called[3][0].name, 'CopyObject')
        self.assertEqual(self.operations_called[4][0].name, 'DeleteObject')

    def test_mv_works_if_outpost_access_point_arn_resolves_to_different_bucket(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3-outposts:us-east-1:123456789012:outpost/"
                   "op-foobar/accesspoint/myaccesspoint/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {"Bucket": "differentbucket"},
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(len(self.operations_called), 4,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'GetAccessPoint')
        self.assertEqual(self.operations_called[1][0].name, 'HeadObject')
        self.assertEqual(self.operations_called[2][0].name, 'CopyObject')
        self.assertEqual(self.operations_called[3][0].name, 'DeleteObject')

    @requires_crt
    def test_mv_works_if_mrap_arn_resolves_to_different_bucket(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://arn:aws:s3::123456789012:accesspoint/foobar.mrap/key "
                   "--validate-same-s3-paths")
        self.parsed_responses = [
            {
                "AccessPoints": [{
                    "Alias": "foobar.mrap",
                    "Regions": [
                        {"Bucket": "differentbucket"},
                    ]
                }]
            },
            self.head_object_response(),
            self.copy_object_response(),
            self.delete_object_response(),
        ]
        self.run_cmd(cmdline, expected_rc=0)
        self.assertEqual(len(self.operations_called), 4,
                         self.operations_called)
        self.assertEqual(self.operations_called[0][0].name, 'ListMultiRegionAccessPoints')
        self.assertEqual(self.operations_called[1][0].name, 'HeadObject')
        self.assertEqual(self.operations_called[2][0].name, 'CopyObject')
        self.assertEqual(self.operations_called[3][0].name, 'DeleteObject')

    def test_skips_validation_if_keys_are_different_accesspoint_arn(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/key2 "
                   "--validate-same-s3-paths")
        self.assert_runs_mv_without_validation(cmdline)

    def test_skips_validation_if_prefixes_are_different_accesspoint_arn(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/prefix/ "
                   "--validate-same-s3-paths")
        self.assert_runs_mv_without_validation(cmdline)

    def test_skips_validation_if_keys_are_different_accesspoint_alias(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://myaccesspoint-foobar-s3alias/key2 "
                   "--validate-same-s3-paths")
        self.assert_runs_mv_without_validation(cmdline)

    def test_skips_validation_if_keys_are_different_outpost_arn(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3-outposts:us-east-1:123456789012:outpost/"
                   "op-foobar/accesspoint/myaccesspoint/key2 "
                   "--validate-same-s3-paths")
        self.assert_runs_mv_without_validation(cmdline)

    def test_skips_validation_if_keys_are_different_outpost_alias(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://myaccesspoint-foobar--op-s3/key2 "
                   "--validate-same-s3-paths")
        self.assert_runs_mv_without_validation(cmdline)

    @requires_crt
    def test_skips_validation_if_keys_are_different_mrap_arn(self):
        cmdline = (f"{self.prefix} s3://bucket/key "
                   "s3://arn:aws:s3::123456789012:accesspoint/foobar.mrap/key2 "
                   "--validate-same-s3-paths")
        self.assert_runs_mv_without_validation(cmdline)

    def test_raises_warning_if_validation_not_set(self):
        cmdline = (f"{self.prefix}s3://bucket/key "
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/key")
        self.assert_raises_warning(cmdline)

    def test_raises_warning_if_validation_not_set_source(self):
        cmdline = (f"{self.prefix}"
                   "s3://arn:aws:s3:us-west-2:123456789012:accesspoint/"
                   "myaccesspoint/key "
                   "s3://bucket/key")
        self.assert_raises_warning(cmdline)
