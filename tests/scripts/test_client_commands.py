import json
import os

import pytest

from infoblox.scripts import cli

pytestmark = pytest.mark.usefixtures('client', 'env_settings')


def test_schema_command_returns_correct_output(runner):
    result = runner.invoke(cli, ['schema'])
    assert 0 == result.exit_code
    captured = result.output
    assert 'requested_version' in captured
    assert 'supported_objects' in captured
    assert 'supported_versions' in captured
    assert 'schema_version' in captured


def test_objects_command_returns_correct_output(runner):
    result = runner.invoke(cli, ['objects'])
    assert 0 == result.exit_code
    captured = result.output
    assert 'ipv4address' in captured
    assert 'ipv6networkcontainer' in captured
    assert 'macfilteraddress' in captured
    assert 'network' in captured


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

        assert 0 == result.exit_code
        assert 'hello' in result.output
        assert 'world' in result.output

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

        assert 0 == result.exit_code
        for item in expected_items:
            assert item in result.output

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

        assert 0 == result.exit_code, result.output
        assert 'hello' in result.output
        assert 'world' in result.output

    def test_command_raises_error_when_no_argument_is_provided(self, runner):
        result = runner.invoke(cli, ['request'])

        assert 2 == result.exit_code
        assert 'Missing argument' in result.output

    def test_command_prints_error_when_infoblox_returns_error(self, responses, url, runner):
        def request_callback(request):
            return 400, {}, request.body

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        result = runner.invoke(cli, ['request', 'foo=bar'])

        assert 0 == result.exit_code
        assert 'foo' in result.output
        assert 'bar' in result.output
