# Copyright 2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
"""Builtin CLI extensions.

This is a collection of built in CLI extensions that can be automatically
registered with the event system.

"""

import awscli.perf_timer as T


def awscli_initialize(event_handlers):
    with T.timer('ImportPlugin.awscli.alias.register_alias_commands'):
        from awscli.alias import register_alias_commands
    with T.timer('ImportPlugin.awscli.argprocess.ParamShorthandParser'):
        from awscli.argprocess import ParamShorthandParser
    with T.timer('ImportPlugin.awscli.clidriver.no_pager_handler'):
        from awscli.clidriver import no_pager_handler
    with T.timer('ImportPlugin.awscli.customizations.datapipeline'):
        from awscli.customizations import datapipeline
    with T.timer('ImportPlugin.awscli.customizations.addexamples.add_examples'):
        from awscli.customizations.addexamples import add_examples
    with T.timer('ImportPlugin.awscli.customizations.argrename.register_arg_renames'):
        from awscli.customizations.argrename import register_arg_renames
    with T.timer('ImportPlugin.awscli.customizations.assumerole.register_assume_role_provider'):
        from awscli.customizations.assumerole import (
            register_assume_role_provider,
        )
    with T.timer('ImportPlugin.awscli.customizations.awslambda.register_lambda_create_function'):
        from awscli.customizations.awslambda import (
            register_lambda_create_function,
        )
    with T.timer('ImportPlugin.awscli.customizations.binaryformat.add_binary_formatter'):
        from awscli.customizations.binaryformat import add_binary_formatter
    with T.timer('ImportPlugin.awscli.customizations.cliinput.register_cli_input_args'):
        from awscli.customizations.cliinput import register_cli_input_args
    with T.timer('ImportPlugin.awscli.customizations.cloudformation.initialize'):
        from awscli.customizations.cloudformation import (
            initialize as cloudformation_init,
        )
    with T.timer('ImportPlugin.awscli.customizations.cloudfront.register'):
        from awscli.customizations.cloudfront import (
            register as register_cloudfront,
        )
    with T.timer('ImportPlugin.awscli.customizations.cloudsearch.initialize'):
        from awscli.customizations.cloudsearch import (
            initialize as cloudsearch_init,
        )
    with T.timer('ImportPlugin.awscli.customizations.cloudsearchdomain.register_cloudsearchdomain'):
        from awscli.customizations.cloudsearchdomain import (
            register_cloudsearchdomain,
        )
    with T.timer('ImportPlugin.awscli.customizations.cloudtrail.initialize'):
        from awscli.customizations.cloudtrail import (
            initialize as cloudtrail_init,
        )
    with T.timer('ImportPlugin.awscli.customizations.codeartifact.register_codeartifact_commands'):
        from awscli.customizations.codeartifact import (
            register_codeartifact_commands,
        )
    with T.timer('ImportPlugin.awscli.customizations.codecommit.initialize'):
        from awscli.customizations.codecommit import (
            initialize as codecommit_init,
        )
    with T.timer('ImportPlugin.awscli.customizations.codedeploy.codedeploy.initialize'):
        from awscli.customizations.codedeploy.codedeploy import (
            initialize as codedeploy_init,
        )
    with T.timer('ImportPlugin.awscli.customizations.configservice.getstatus.register_get_status'):
        from awscli.customizations.configservice.getstatus import (
            register_get_status,
        )
    with T.timer('ImportPlugin.awscli.customizations.configservice.putconfigurationrecorder.register_modify_put_configuration_recorder'):
        from awscli.customizations.configservice.putconfigurationrecorder import (
            register_modify_put_configuration_recorder,
        )
    with T.timer('ImportPlugin.awscli.customizations.configservice.rename_cmd.register_rename_config'):
        from awscli.customizations.configservice.rename_cmd import (
            register_rename_config,
        )
    with T.timer('ImportPlugin.awscli.customizations.configservice.subscribe.register_subscribe'):
        from awscli.customizations.configservice.subscribe import (
            register_subscribe,
        )
    with T.timer('ImportPlugin.awscli.customizations.configure.configure.register_configure_cmd'):
        from awscli.customizations.configure.configure import (
            register_configure_cmd,
        )
    with T.timer('ImportPlugin.awscli.customizations.devcommands.register_dev_commands'):
        from awscli.customizations.devcommands import register_dev_commands
    with T.timer('ImportPlugin.awscli.customizations.dlm.dlm.dlm_initialize'):
        from awscli.customizations.dlm.dlm import dlm_initialize
    with T.timer('ImportPlugin.awscli.customizations.dsql.register_dsql_customizations'):
        from awscli.customizations.dsql import register_dsql_customizations
    with T.timer('ImportPlugin.awscli.customizations.dynamodb.ddb.register_ddb'):
        from awscli.customizations.dynamodb.ddb import register_ddb
    with T.timer('ImportPlugin.awscli.customizations.dynamodb.paginatorfix.register_dynamodb_paginator_fix'):
        from awscli.customizations.dynamodb.paginatorfix import (
            register_dynamodb_paginator_fix,
        )
    with T.timer('ImportPlugin.awscli.customizations.ec2.addcount.register_count_events'):
        from awscli.customizations.ec2.addcount import register_count_events
    with T.timer('ImportPlugin.awscli.customizations.ec2.bundleinstance.register_bundleinstance'):
        from awscli.customizations.ec2.bundleinstance import (
            register_bundleinstance,
        )
    with T.timer('ImportPlugin.awscli.customizations.ec2.decryptpassword.ec2_add_priv_launch_key'):
        from awscli.customizations.ec2.decryptpassword import (
            ec2_add_priv_launch_key,
        )
    with T.timer('ImportPlugin.awscli.customizations.ec2.paginate.register_ec2_page_size_injector'):
        from awscli.customizations.ec2.paginate import (
            register_ec2_page_size_injector,
        )
    with T.timer('ImportPlugin.awscli.customizations.ec2.protocolarg.register_protocol_args'):
        from awscli.customizations.ec2.protocolarg import (
            register_protocol_args,
        )
    with T.timer('ImportPlugin.awscli.customizations.ec2.runinstances.register_runinstances'):
        from awscli.customizations.ec2.runinstances import register_runinstances
    with T.timer('ImportPlugin.awscli.customizations.ec2.secgroupsimplify.register_secgroup'):
        from awscli.customizations.ec2.secgroupsimplify import (
            register_secgroup,
        )
    with T.timer('ImportPlugin.awscli.customizations.ec2instanceconnect.register_ec2_instance_connect_commands'):
        from awscli.customizations.ec2instanceconnect import (
            register_ec2_instance_connect_commands,
        )
    with T.timer('ImportPlugin.awscli.customizations.ecr.register_ecr_commands'):
        from awscli.customizations.ecr import register_ecr_commands
    with T.timer('ImportPlugin.awscli.customizations.ecr_public.register_ecr_public_commands'):
        from awscli.customizations.ecr_public import (
            register_ecr_public_commands,
        )
    with T.timer('ImportPlugin.awscli.customizations.ecs.initialize'):
        from awscli.customizations.ecs import initialize as ecs_initialize
    with T.timer('ImportPlugin.awscli.customizations.ecs.monitormutatinggatewayservice.register_monitor_mutating_gateway_service'):
        from awscli.customizations.ecs.monitormutatinggatewayservice import (
            register_monitor_mutating_gateway_service,
        )
    with T.timer('ImportPlugin.awscli.customizations.eks.initialize'):
        from awscli.customizations.eks import initialize as eks_initialize
    with T.timer('ImportPlugin.awscli.customizations.emr.emr.emr_initialize'):
        from awscli.customizations.emr.emr import emr_initialize
    with T.timer('ImportPlugin.awscli.customizations.emrcontainers.initialize'):
        from awscli.customizations.emrcontainers import (
            initialize as emrcontainers_initialize,
        )
    with T.timer('ImportPlugin.awscli.customizations.gamelift.register_gamelift_commands'):
        from awscli.customizations.gamelift import register_gamelift_commands
    with T.timer('ImportPlugin.awscli.customizations.generatecliskeleton.register_generate_cli_skeleton'):
        from awscli.customizations.generatecliskeleton import (
            register_generate_cli_skeleton,
        )
    with T.timer('ImportPlugin.awscli.customizations.globalargs.register_parse_global_args'):
        from awscli.customizations.globalargs import register_parse_global_args
    with T.timer('ImportPlugin.awscli.customizations.history.register_history_commands'):
        from awscli.customizations.history import (
            register_history_commands,
            register_history_mode,
        )
    with T.timer('ImportPlugin.awscli.customizations.iamvirtmfa.IAMVMFAWrapper'):
        from awscli.customizations.iamvirtmfa import IAMVMFAWrapper
    with T.timer('ImportPlugin.awscli.customizations.iot.register_create_keys_and_cert_arguments'):
        from awscli.customizations.iot import (
            register_create_keys_and_cert_arguments,
            register_create_keys_from_csr_arguments,
        )
    with T.timer('ImportPlugin.awscli.customizations.iot_data.register_custom_endpoint_note'):
        from awscli.customizations.iot_data import (
            register_custom_endpoint_note,
        )
    with T.timer('ImportPlugin.awscli.customizations.kinesis.register_kinesis_list_streams_pagination_backcompat'):
        from awscli.customizations.kinesis import (
            register_kinesis_list_streams_pagination_backcompat,
        )
    with T.timer('ImportPlugin.awscli.customizations.kms.register_fix_kms_create_grant_docs'):
        from awscli.customizations.kms import (
            register_fix_kms_create_grant_docs,
        )
    with T.timer('ImportPlugin.awscli.customizations.lightsail.initialize'):
        from awscli.customizations.lightsail import (
            initialize as lightsail_initialize,
        )
    with T.timer('ImportPlugin.awscli.customizations.login.register_login_cmds'):
        from awscli.customizations.login import register_login_cmds
    with T.timer('ImportPlugin.awscli.customizations.logs.register_logs_commands'):
        from awscli.customizations.logs import register_logs_commands
    with T.timer('ImportPlugin.awscli.customizations.paginate.register_pagination'):
        from awscli.customizations.paginate import register_pagination
    with T.timer('ImportPlugin.awscli.customizations.putmetricdata.register_put_metric_data'):
        from awscli.customizations.putmetricdata import register_put_metric_data
    with T.timer('ImportPlugin.awscli.customizations.quicksight.register_quicksight_asset_bundle_customizations'):
        from awscli.customizations.quicksight import (
            register_quicksight_asset_bundle_customizations,
        )
    with T.timer('ImportPlugin.awscli.customizations.rds.register_add_generate_db_auth_token'):
        from awscli.customizations.rds import (
            register_add_generate_db_auth_token,
            register_rds_modify_split,
        )
    with T.timer('ImportPlugin.awscli.customizations.rekognition.register_rekognition_detect_labels'):
        from awscli.customizations.rekognition import (
            register_rekognition_detect_labels,
        )
    with T.timer('ImportPlugin.awscli.customizations.removals.register_removals'):
        from awscli.customizations.removals import register_removals
    with T.timer('ImportPlugin.awscli.customizations.route53.register_create_hosted_zone_doc_fix'):
        from awscli.customizations.route53 import (
            register_create_hosted_zone_doc_fix,
        )
    with T.timer('ImportPlugin.awscli.customizations.s3.s3.s3_plugin_initialize'):
        from awscli.customizations.s3.s3 import s3_plugin_initialize
    with T.timer('ImportPlugin.awscli.customizations.s3errormsg.register_s3_error_msg'):
        from awscli.customizations.s3errormsg import register_s3_error_msg
    with T.timer('ImportPlugin.awscli.customizations.s3events.register_document_expires_string'):
        from awscli.customizations.s3events import (
            register_document_expires_string,
            register_event_stream_arg,
        )
    with T.timer('ImportPlugin.awscli.customizations.servicecatalog.register_servicecatalog_commands'):
        from awscli.customizations.servicecatalog import (
            register_servicecatalog_commands,
        )
    with T.timer('ImportPlugin.awscli.customizations.sessendemail.register_ses_send_email'):
        from awscli.customizations.sessendemail import register_ses_send_email
    with T.timer('ImportPlugin.awscli.customizations.sessionmanager.register_ssm_session'):
        from awscli.customizations.sessionmanager import register_ssm_session
    with T.timer('ImportPlugin.awscli.customizations.sso.register_sso_commands'):
        from awscli.customizations.sso import register_sso_commands
    with T.timer('ImportPlugin.awscli.customizations.streamingoutputarg.add_streaming_output_arg'):
        from awscli.customizations.streamingoutputarg import (
            add_streaming_output_arg,
        )
    with T.timer('ImportPlugin.awscli.customizations.timestampformat.register_timestamp_format'):
        from awscli.customizations.timestampformat import (
            register_timestamp_format,
        )
    with T.timer('ImportPlugin.awscli.customizations.toplevelbool.register_bool_params'):
        from awscli.customizations.toplevelbool import register_bool_params
    with T.timer('ImportPlugin.awscli.customizations.translate.register_translate_import_terminology'):
        from awscli.customizations.translate import (
            register_translate_import_terminology,
        )
    with T.timer('ImportPlugin.awscli.customizations.waiters.register_add_waiters'):
        from awscli.customizations.waiters import register_add_waiters
    with T.timer('ImportPlugin.awscli.customizations.wizard.commands.register_wizard_commands'):
        from awscli.customizations.wizard.commands import (
            register_wizard_commands,
        )
    with T.timer('ImportPlugin.awscli.paramfile.register_uri_param_handler'):
        from awscli.paramfile import register_uri_param_handler

    with T.timer('InitPlugin.awscli.paramfile.register_uri_param_handler'):
        event_handlers.register('session-initialized', register_uri_param_handler)
    with T.timer('InitPlugin.awscli.customizations.binaryformat.add_binary_formatter'):
        event_handlers.register('session-initialized', add_binary_formatter)
    with T.timer('InitPlugin.awscli.clidriver.no_pager_handler'):
        event_handlers.register('session-initialized', no_pager_handler)
    with T.timer('InitPlugin.awscli.argprocess.ParamShorthandParser'):
        param_shorthand = ParamShorthandParser()
        event_handlers.register('process-cli-arg', param_shorthand)
    # The s3 error mesage needs to registered before the
    # generic error handler.
    with T.timer('InitPlugin.awscli.customizations.s3errormsg.register_s3_error_msg'):
        register_s3_error_msg(event_handlers)
    #    # The following will get fired for every option we are
    #    # documenting.  It will attempt to add an example_fn on to
    #    # the parameter object if the parameter supports shorthand
    #    # syntax.  The documentation event handlers will then use
    #    # the examplefn to generate the sample shorthand syntax
    #    # in the docs.  Registering here should ensure that this
    #    # handler gets called first but it still feels a bit brittle.
    #    event_handlers.register('doc-option-example.*.*.*',
    #                            param_shorthand.add_example_fn)
    with T.timer('InitPlugin.awscli.customizations.addexamples.add_examples'):
        event_handlers.register('doc-examples.*.*', add_examples)
    with T.timer('InitPlugin.awscli.customizations.cliinput.register_cli_input_args'):
        register_cli_input_args(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.streamingoutputarg.add_streaming_output_arg'):
        event_handlers.register(
            'building-argument-table.*', add_streaming_output_arg
        )
    with T.timer('InitPlugin.awscli.customizations.ec2.addcount.register_count_events'):
        register_count_events(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2.decryptpassword.ec2_add_priv_launch_key'):
        event_handlers.register(
            'building-argument-table.ec2.get-password-data',
            ec2_add_priv_launch_key,
        )
    with T.timer('InitPlugin.awscli.customizations.globalargs.register_parse_global_args'):
        register_parse_global_args(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.paginate.register_pagination'):
        register_pagination(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2.secgroupsimplify.register_secgroup'):
        register_secgroup(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2.bundleinstance.register_bundleinstance'):
        register_bundleinstance(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.s3.s3.s3_plugin_initialize'):
        s3_plugin_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.dynamodb.ddb.register_ddb'):
        register_ddb(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2.runinstances.register_runinstances'):
        register_runinstances(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.removals.register_removals'):
        register_removals(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.rds.register_rds_modify_split'):
        register_rds_modify_split(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.rekognition.register_rekognition_detect_labels'):
        register_rekognition_detect_labels(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.rds.register_add_generate_db_auth_token'):
        register_add_generate_db_auth_token(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.dsql.register_dsql_customizations'):
        register_dsql_customizations(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.putmetricdata.register_put_metric_data'):
        register_put_metric_data(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.sessendemail.register_ses_send_email'):
        register_ses_send_email(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.iamvirtmfa.IAMVMFAWrapper'):
        IAMVMFAWrapper(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.argrename.register_arg_renames'):
        register_arg_renames(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.configure.configure.register_configure_cmd'):
        register_configure_cmd(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.cloudtrail.initialize'):
        cloudtrail_init(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ecr.register_ecr_commands'):
        register_ecr_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ecr_public.register_ecr_public_commands'):
        register_ecr_public_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.toplevelbool.register_bool_params'):
        register_bool_params(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2.protocolarg.register_protocol_args'):
        register_protocol_args(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.datapipeline.register_customizations'):
        datapipeline.register_customizations(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.cloudsearch.initialize'):
        cloudsearch_init(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.emr.emr.emr_initialize'):
        emr_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.emrcontainers.initialize'):
        emrcontainers_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.eks.initialize'):
        eks_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ecs.initialize'):
        ecs_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ecs.monitormutatinggatewayservice.register_monitor_mutating_gateway_service'):
        register_monitor_mutating_gateway_service(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.lightsail.initialize'):
        lightsail_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.cloudsearchdomain.register_cloudsearchdomain'):
        register_cloudsearchdomain(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.generatecliskeleton.register_generate_cli_skeleton'):
        register_generate_cli_skeleton(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.assumerole.register_assume_role_provider'):
        register_assume_role_provider(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.waiters.register_add_waiters'):
        register_add_waiters(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.codedeploy.codedeploy.initialize'):
        codedeploy_init(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.configservice.subscribe.register_subscribe'):
        register_subscribe(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.configservice.getstatus.register_get_status'):
        register_get_status(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.configservice.rename_cmd.register_rename_config'):
        register_rename_config(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.timestampformat.register_timestamp_format'):
        register_timestamp_format(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.awslambda.register_lambda_create_function'):
        register_lambda_create_function(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.kms.register_fix_kms_create_grant_docs'):
        register_fix_kms_create_grant_docs(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.route53.register_create_hosted_zone_doc_fix'):
        register_create_hosted_zone_doc_fix(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.configservice.putconfigurationrecorder.register_modify_put_configuration_recorder'):
        register_modify_put_configuration_recorder(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.codeartifact.register_codeartifact_commands'):
        register_codeartifact_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.codecommit.initialize'):
        codecommit_init(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.iot_data.register_custom_endpoint_note'):
        register_custom_endpoint_note(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.iot.register_create_keys_and_cert_arguments'):
        event_handlers.register(
            'building-argument-table.iot.create-keys-and-certificate',
            register_create_keys_and_cert_arguments,
        )
    with T.timer('InitPlugin.awscli.customizations.iot.register_create_keys_from_csr_arguments'):
        event_handlers.register(
            'building-argument-table.iot.create-certificate-from-csr',
            register_create_keys_from_csr_arguments,
        )
    with T.timer('InitPlugin.awscli.customizations.cloudfront.register'):
        register_cloudfront(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.gamelift.register_gamelift_commands'):
        register_gamelift_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2.paginate.register_ec2_page_size_injector'):
        register_ec2_page_size_injector(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.cloudformation.initialize'):
        cloudformation_init(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.servicecatalog.register_servicecatalog_commands'):
        register_servicecatalog_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.translate.register_translate_import_terminology'):
        register_translate_import_terminology(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.history.register_history_mode'):
        register_history_mode(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.history.register_history_commands'):
        register_history_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.s3events.register_event_stream_arg'):
        register_event_stream_arg(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.s3events.register_document_expires_string'):
        register_document_expires_string(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.dlm.dlm.dlm_initialize'):
        dlm_initialize(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.sessionmanager.register_ssm_session'):
        register_ssm_session(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.logs.register_logs_commands'):
        register_logs_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.devcommands.register_dev_commands'):
        register_dev_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.wizard.commands.register_wizard_commands'):
        register_wizard_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.sso.register_sso_commands'):
        register_sso_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.dynamodb.paginatorfix.register_dynamodb_paginator_fix'):
        register_dynamodb_paginator_fix(event_handlers)
    with T.timer('InitPlugin.awscli.alias.register_alias_commands'):
        register_alias_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.kinesis.register_kinesis_list_streams_pagination_backcompat'):
        register_kinesis_list_streams_pagination_backcompat(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.quicksight.register_quicksight_asset_bundle_customizations'):
        register_quicksight_asset_bundle_customizations(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.ec2instanceconnect.register_ec2_instance_connect_commands'):
        register_ec2_instance_connect_commands(event_handlers)
    with T.timer('InitPlugin.awscli.customizations.login.register_login_cmds'):
        register_login_cmds(event_handlers)
