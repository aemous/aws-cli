PLUGINS_REGISTRY = {
    '__main__': [
        ('awscli.customizations.cliinput', 'register_cli_input_args'),
        ('awscli.customizations.paginate', 'register_pagination'),
        ('awscli.customizations.generatecliskeleton', 'register_generate_cli_skeleton'),
        ('awscli.customizations.streamingoutputarg', 'register_streaming_output_arg'),
        ('awscli.customizations.waiters', 'register_add_waiters'),
        ('awscli.alias', 'register_alias_commands'),
        ('awscli.argprocess', 'register_param_shorthand_parser'),
        ('awscli.paramfile', 'register_param_handler_session'),
        ('awscli.customizations.binaryformat', 'register_binary_formatter'),
        ('awscli.clidriver', 'register_no_pager_handler'),
        ('awscli.customizations.assumerole', 'register_assume_role_provider'),
        ('awscli.customizations.timestampformat', 'register_timestamp_format'),
        ('awscli.customizations.history', 'register_history_mode'),
        ('awscli.customizations.sso', 'register_sso_commands'),
        ('awscli.customizations.globalargs', 'register_parse_global_args')
    ]
}