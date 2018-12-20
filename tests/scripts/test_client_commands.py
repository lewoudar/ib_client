import json
import os

import pytest

from infoblox.scripts import cli
from tests.helpers import assert_list_items, assert_in_output

pytestmark = pytest.mark.usefixtures('client', 'env_settings')


def test_schema_command_returns_correct_output(runner):
    result = runner.invoke(cli, ['schema'])
    assert_list_items(0, ['requested_version', 'supported_objects', 'supported_versions', 'schema_version'], result)


def test_objects_command_returns_correct_output(runner):
    result = runner.invoke(cli, ['objects'])
    assert_list_items(0, ['ipv4address', 'ipv6networkcontainer', 'macfilteraddress', 'network'], result)


class TestRequestCommand:
    # test request command
    def test_command_returns_correct_output_with_option_parameter(self, responses, url, tempdir, runner):
        expected_data = {'hello': 'world'}

        def request_callback(*_):
            return 200, {}, json.dumps(expected_data)

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        filename = os.path.join(tempdir, 'foo.json')
        with open(filename, 'w') as f:
            json.dump({'foo': 'bar'}, f)
        result = runner.invoke(cli, ['request', '-j', filename])

        assert_list_items(0, ['hello', 'world'], result)

    @pytest.mark.parametrize(('input_data', 'expected_items'), [
        ('foo=bar', ['foo', 'bar']),
        ('{"foo":"bar"}', ['foo', 'bar']),
        ('foo=bar shoes:=2', ['foo', 'bar', 'shoes', '2'])
    ])
    def test_command_returns_correct_output_with_argument_parameter(self, responses, url, runner, input_data,
                                                                    expected_items):
        def request_callback(request):
            return 200, {}, request.body

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        result = runner.invoke(cli, ['request', input_data])

        assert_list_items(0, expected_items, result)

    @pytest.mark.parametrize(('json_file', 'command_options'), [
        ('hello.json', ['-j', 'hello.json', 'foo=bar']),
        ('hello.json', ['foo=bar', '-j', 'hello.json'])
    ])
    def test_command_prioritizes_option_over_argument(self, responses, url, tempdir, runner, json_file,
                                                      command_options):
        def request_callback(request):
            return 200, {}, request.body

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        filename = os.path.join(tempdir, json_file)
        with open(filename, 'w') as f:
            json.dump({'hello': 'world'}, f)
        # we realize a little trick to give the correct path of created file
        index = command_options.index(json_file)
        command_options[index] = filename
        result = runner.invoke(cli, ['request', *command_options])

        assert_list_items(0, ['hello', 'world'], result)

    def test_command_raises_error_when_no_argument_is_provided(self, runner):
        result = runner.invoke(cli, ['request'])

        assert_in_output(2, 'Missing argument', result)

    def test_command_prints_error_when_infoblox_returns_error(self, responses, url, runner):
        def request_callback(request):
            return 400, {}, request.body

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        result = runner.invoke(cli, ['request', 'foo=bar'])

        assert_list_items(0, ['foo', 'bar'], result)
