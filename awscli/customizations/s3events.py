# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
"""Add S3 specific event streaming output arg."""
from awscli.arguments import CustomArgument


STREAM_HELP_TEXT = 'Filename where the records will be saved'


class DocSectionNotFoundError(Exception):
    pass


def register_event_stream_arg(event_handlers):
    event_handlers.register(
        'building-argument-table.s3api.select-object-content',
        add_event_stream_output_arg)

    event_handlers.register_last(
        'doc-output.s3api.select-object-content',
        replace_event_stream_docs
    )


def register_document_expires_string(event_handlers):
    event_handlers.register_last(
        'doc-output.s3api',
        document_expires_string
    )


def add_event_stream_output_arg(argument_table, operation_model,
                                session, **kwargs):
    argument_table['outfile'] = S3SelectStreamOutputArgument(
        name='outfile', help_text=STREAM_HELP_TEXT,
        cli_type_name='string', positional_arg=True,
        stream_key=operation_model.output_shape.serialization['payload'],
        session=session)


def replace_event_stream_docs(help_command, **kwargs):
    doc = help_command.doc
    current = ''
    while current != '======\nOutput\n======':
        try:
            current = doc.pop_write()
        except IndexError:
            # This should never happen, but in the rare case that it does
            # we should be raising something with a helpful error message.
            raise DocSectionNotFoundError(
                'Could not find the "output" section for the command: %s'
                % help_command)
    doc.write('======\nOutput\n======\n')
    doc.write("This command generates no output.  The selected "
              "object content is written to the specified outfile.\n")


def document_expires_string(help_command, **kwargs):
    doc = help_command.doc
    caught_index_error = False
    popped = []
    current = ''
    while current != 'Expires -> (timestamp)':
        try:
            current = doc.pop_write()
            popped.append(current)
        except IndexError:
            # Do nothing if Expires is not in the modeled response
            caught_index_error = True
            break

    # Only inject the deprecation notice if the Expires timestamp arg was found in the document
    if not caught_index_error:
        # Put back the expires field and description
        doc.push_write(popped.pop())
        doc.push_write(popped.pop())
        doc.push_write(popped.pop())
        doc.push_write(popped.pop())

        doc.push_write('\n\n\n' + doc.style.spaces())
        doc.push_write('.. note::')
        doc.style.indent()
        doc.push_write('\n\n\n' + doc.style.spaces())
        doc.push_write('This member has been deprecated. Please use `ExpiresString` instead.\n')
        doc.style.dedent()
        doc.push_write('\n\n' + doc.style.spaces())

        doc.push_write('\n\n' + doc.style.spaces())
        doc.push_write('ExpiresString -> (string)\n\n')
        doc.push_write('\tThe raw, unparsed value of the ``Expires`` field.')
        doc.push_write('\n\n' + doc.style.spaces())

    # Write rest of document
    while len(popped) > 0:
        doc.push_write(popped.pop())


class S3SelectStreamOutputArgument(CustomArgument):
    _DOCUMENT_AS_REQUIRED = True

    def __init__(self, stream_key, session, **kwargs):
        super(S3SelectStreamOutputArgument, self).__init__(**kwargs)
        # This is the key in the response body where we can find the
        # streamed contents.
        self._stream_key = stream_key
        self._output_file = None
        self._session = session

    def add_to_params(self, parameters, value):
        self._output_file = value
        self._session.register('after-call.s3.SelectObjectContent',
                               self.save_file)

    def save_file(self, parsed, **kwargs):
        # This method is hooked into after-call which fires
        # before the error checking happens in the client.
        # Therefore if the stream_key is not in the parsed
        # response we immediately return and let the default
        # error handling happen.
        if self._stream_key not in parsed:
            return
        event_stream = parsed[self._stream_key]
        with open(self._output_file, 'wb') as fp:
            for event in event_stream:
                if 'Records' in event:
                    fp.write(event['Records']['Payload'])
        # We don't want to include the streaming param in
        # the returned response, it's not JSON serializable.
        del parsed[self._stream_key]
