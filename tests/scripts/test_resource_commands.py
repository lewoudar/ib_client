import json
from datetime import datetime, timedelta

import pytest

from infoblox.scripts import cli

from tests.helpers import assert_list_items, assert_in_output

pytestmark = pytest.mark.usefixtures('client', 'resource', 'env_settings')


@pytest.fixture(scope='module')
def cud_options():
    """Common options for create, update and delete operations"""
    action_date_time = datetime.now() + timedelta(hours=1)
    action_timestamp = int(action_date_time.timestamp())
    return ['--schedule-time', action_timestamp, '--schedule-now', 'false', '--schedule-predecessor-task', 'foo',
            '--schedule-warn-level', 'WARN', '--approval-comment', 'yes', '--approval-query-mode', 'false',
            '--approval-ticket-number', '45']


# Actually, I don't know how to test the group alone, so I use tests on documentation command
# to check name group option

def test_option_name_is_prompted_when_missing(runner, resource_name):
    result = runner.invoke(cli, ['object', 'documentation'], input=f'{resource_name}\n')

    assert 0 == result.exit_code


def test_object_command_raises_exception_when_object_name_is_unknown(runner):
    wapi_object = 'foo'
    result = runner.invoke(cli, ['object', '-n', wapi_object, 'documentation'])

    assert_in_output(2, f'{wapi_object} is not a valid infoblox object', result)


@pytest.mark.parametrize('name_option', ['-n', '--name'])
def test_documentation_command_returns_correct_output(runner, resource_name, name_option):
    result = runner.invoke(cli, ['object', name_option, resource_name, 'documentation'])

    assert_list_items(0, ['type', 'fields', 'version', 'wapi_primitive'], result)


def test_fields_command_prints_correct_output(runner, resource_name):
    result = runner.invoke(cli, ['object', '-n', resource_name, 'fields'])

    assert_list_items(0, ['comment', 'network'], result)


def test_functions_command_prints_correct_output(runner, resource_name):
    result = runner.invoke(cli, ['object', '-n', resource_name, 'functions'])

    assert_list_items(0, ['next_available_ip', 'expand_network'], result)


class TestGetFieldInfoCommand:
    # test get_field_information command function
    @pytest.mark.parametrize('name_option', ['-n', '--name'])
    def test_command_prints_correct_output(self, runner, resource_name, name_option):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'field-info', name_option, 'network'])

        assert_list_items(0, ['doc', 'is_array', 'name', 'standard_field'], result)

    def test_command_prompts_field_name_when_option_is_missing(self, runner, resource_name):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'field-info'], input='network\n')

        assert 0 == result.exit_code

    def test_command_raises_error_when_field_name_is_unknown(self, runner, resource_name):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'field-info', '-n', 'foo'])

        assert_in_output(2, 'does not exist', result)


class TestGetFunctionInfoCommand:
    # test get_function_information command function
    @pytest.mark.parametrize('name_option', ['-n', '--name'])
    def test_command_prints_correct_output(self, runner, resource_name, name_option):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-info', name_option, 'next_available_ip'])

        assert_list_items(0, ['doc', 'schema', 'name', 'supports', 'wapi_primitive'], result)

    def test_commands_prompts_function_name_when_option_is_missing(self, runner, resource_name):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-info'], input='next_available_ip\n')

        assert 0 == result.exit_code

    def test_commands_raises_error_when_function_name_is_unknown(self, runner, resource_name):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-info', '-n', 'foo'])

        assert_in_output(2, 'does not exist', result)


class TestGetCommand:

    def test_command_prints_correct_output_giving_object_reference(self, runner, responses, url):
        object_ref = 'network/just-a-network:10.2.0.0%2F16'
        responses.add(responses.GET, f'{url}/{object_ref}', json={'network': '10.2.0.0/16', 'comment': 'foo'},
                      status=200)
        result = runner.invoke(cli, ['object', '-n', 'network', 'get', '-o', object_ref, '--return-fields',
                                     'network,comment', '--proxy-search', 'GM'])

        assert_list_items(0, ['network', '10.2.0.0/16'], result)

    def test_command_prints_correct_output_without_object_reference(self, runner, responses, url, resource_name):
        response_data = {'network': '10.2.0.0/16', 'comment': 'foo'}
        responses.add(responses.GET, f'{url}/{resource_name}', json=[response_data], status=200)
        result = runner.invoke(cli, ['object', '-n', resource_name, 'get', '-p', '{"network": "10.2.0.0/16"}',
                                     '--return-fields-plus', 'authority', '--proxy-search', 'LOCAL'])

        items_to_test = []
        for key, value in response_data.items():
            items_to_test.append(key)
            items_to_test.append(value)
        assert_list_items(0, items_to_test, result)

    def test_command_prints_error_if_response_status_code_greater_or_equal_than_400(self, runner, responses, url,
                                                                                    resource_name):
        object_ref = 'network/just-a-network:10.2.0.0%2F16'
        responses.add(responses.GET, f'{url}/{object_ref}', json={'error': 'oops'}, status=400)
        result = runner.invoke(cli, ['object', '-n', resource_name, 'get', '-o', object_ref])

        assert_list_items(0, ['error', 'oops'], result)

    @pytest.mark.parametrize(('options', 'error_message'), [
        (['-p', '{"authority": true}'], 'authority is not searchable'),
        (['--return-fields-plus', 'contains_address'], 'contains_address is a search only field')
    ])
    def test_command_raises_error_when_other_intern_errors_happened(self, runner, resource_name, options,
                                                                    error_message):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'get'] + options)

        assert_in_output(2, error_message, result)


class TestCountCommand:
    @pytest.mark.parametrize(('networks', 'expected_output'), [
        ([{'network': f'192.168.{i}.0/24'} for i in range(1, 5)], '4'),
        ([], '0'),
    ])
    def test_command_prints_correct_output(self, runner, responses, url, resource_name, networks, expected_output):
        responses.add(responses.GET, f'{url}/{resource_name}', json={'result': networks}, status=200)
        result = runner.invoke(cli, ['object', '-n', resource_name, 'count', '-p', '{"network~": "192."}',
                                     '--proxy-search', 'LOCAL'])

        assert_in_output(0, expected_output, result)

    def test_command_prints_error_if_response_status_code_greater_or_equal_than_400(self, runner, responses, url,
                                                                                    resource_name):
        responses.add(responses.GET, f'{url}/{resource_name}', json={'error': 'oops'}, status=400)
        result = runner.invoke(cli, ['object', '-n', resource_name, 'count'])

        assert_list_items(0, ['error', 'oops'], result)

    def test_command_raises_error_when_other_intern_errors_happened(self, runner, resource_name):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'count', '-p', '{"authority": true}'])

        assert_in_output(2, 'authority is not searchable', result)


class TestFunctionCallCommand:
    @pytest.mark.parametrize('options', [
        ['-n', 'next_available_ip', '-a', '{"num":1}'],
        ['--name', 'next_available_ip', '--arguments', '{"num":1}']
    ])
    def test_command_prints_correct_output_with_object_ref(self, runner, responses, url, resource_name, options):
        object_ref = 'foo'
        expected_response = {'ips': ['192.168.1.1']}

        def request_callback(*_):
            return 200, {}, json.dumps(expected_response)

        responses.add_callback(responses.POST, f'{url}/{object_ref}', callback=request_callback,
                               content_type='application/json')
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-call', '-o', object_ref] + options)

        assert_list_items(0, ['ips', '192.168.1.1'], result)

    @pytest.mark.usefixtures('fileop_resource')
    def test_command_prints_correct_output_without_object_ref(self, runner, responses, url):
        expected_response = {'token': 'my-token', 'url': 'http://foobar.com'}
        resource_name = 'fileop'

        def request_callback(*_):
            return 200, {}, json.dumps(expected_response)

        # since the resource fixture is called on every test, we need to perform the next action to prevent
        # having an api call not detected by responses utility.
        responses.remove(responses.GET, f'{url}/network')
        responses.add_callback(responses.POST, f'{url}/{resource_name}', callback=request_callback,
                               content_type='application/json')
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-call', '-n', 'uploadinit', '-a', '{}'])

        assert_list_items(0, ['token', 'my-token', 'url', 'http://foobar.com'], result)

    def test_command_prints_error_if_response_status_code_greater_or_equal_than_400(self, runner, responses, url,
                                                                                    resource_name):
        def request_callback(*_):
            return 400, {}, json.dumps({'error': 'oops'})

        object_ref = 'foo'
        responses.add_callback(responses.POST, f'{url}/{object_ref}', callback=request_callback,
                               content_type='application/json')
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-call', '-o', object_ref, '-n',
                                     'next_available_ip', '-a', '{"num":1}'])

        assert_list_items(0, ['error', 'oops'], result)

    @pytest.mark.parametrize(('options', 'error_message'), [
        (['-n', 'bar', '-a', '{"num":1}'], 'is an unknown function'),
        (['-n', 'next_available_ip', '-a', '{"bar":1}'], 'is not a valid argument for next_available_ip function')
    ])
    def test_command_raises_error_when_other_intern_errors_happened(self, runner, resource_name, options,
                                                                    error_message):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'func-call', '-o', 'foo'] + options)

        assert_in_output(2, error_message, result)


class TestCreateCommand:
    @pytest.mark.parametrize('return_fields_option', [
        ['--return-fields', 'network,comment'],
        ['--return-fields-plus', 'authority,ipv4addr']
    ])
    def test_command_prints_correct_output(self, runner, responses, url, resource_name, cud_options,
                                           return_fields_option):
        expected_response = {
            '_ref': 'network/just-a-string:192.168.1.0/24',
            'network': '192.168.1.0/24',
            'comment': 'new network'
        }

        def request_callback(*_):
            return 201, {}, json.dumps(expected_response)

        responses.add_callback(responses.POST, f'{url}/{resource_name}', callback=request_callback,
                               content_type='application/json')
        result = runner.invoke(cli, ['object', '-n', resource_name, 'create', '--arguments',
                                     '{"network":"192.168.1.0/24"}'] + return_fields_option + cud_options)

        items_to_test = []
        for key, value in expected_response.items():
            items_to_test.append(key)
            items_to_test.append(value)
        assert_list_items(0, items_to_test, result)

    def test_command_prints_error_if_response_status_code_greater_or_equal_than_400(self, runner, responses, url,
                                                                                    resource_name):
        def request_callback(*_):
            return 400, {}, json.dumps({'error': 'oops'})

        responses.add_callback(responses.POST, f'{url}/{resource_name}', callback=request_callback,
                               content_type='application/json')
        result = runner.invoke(cli, ['object', '-n', resource_name, 'create', '-a', '{"network":"192.168.1.0/24"}'])

        assert_list_items(0, ['error', 'oops'], result)

    @pytest.mark.parametrize(('options', 'error_message'), [
        (['-a', '{"network":"192.168.1.0/24","foo":15}'], 'foo is not a network field'),
        (['--schedule-time', '150', '-a', '{"network":"192.168.1.0/24"}'], 'schedule_time must be a positive'
                                                                           ' integer representing a FUTURE TIME')
    ])
    def test_command_raises_error_when_other_intern_errors_happened(self, runner, resource_name, options,
                                                                    error_message):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'create'] + options)

        assert_in_output(2, error_message, result)


class TestUpdateCommand:
    @pytest.mark.parametrize('return_fields_option', [
        ['--return-fields', 'network,comment'],
        ['--return-fields-plus', 'authority,ipv4addr']
    ])
    def test_command_prints_correct_output(self, runner, responses, url, resource_name, cud_options,
                                           return_fields_option):
        object_ref = 'network:updated-object:192.168.1.0/24'
        comment = 'updated comment'
        network = '192.168.1.0/24'

        def request_callback(request):
            payload = json.loads(request.body)
            data = {
                '_ref': object_ref,
                'comment': payload['comment'],
                'network': network
            }
            return 200, {}, json.dumps(data)

        responses.add_callback(responses.PUT, f'{url}/{object_ref}', callback=request_callback,
                               content_type='application/json')

        result = runner.invoke(cli, [
            *['object', '-n', resource_name, 'update', '-o', object_ref, '-a', json.dumps({'comment': comment})],
            *return_fields_option, *cud_options
        ])

        assert 0 == result.exit_code, result.output
        assert_list_items(0, ['_ref', 'comment', 'network', comment, network, object_ref], result)

    def test_command_prints_error_if_response_status_code_greater_or_equal_than_400(self, runner, responses, url,
                                                                                    resource_name):
        def request_callback(*_):
            return 400, {}, json.dumps({'error': 'oops'})

        object_ref = 'object-ref'
        responses.add_callback(responses.PUT, f'{url}/{object_ref}', callback=request_callback,
                               content_type='application/json')
        result = runner.invoke(cli, ['object', '-n', resource_name, 'update', '-o', object_ref,
                                     '-a', '{"comment":"bar"}'])

        assert_list_items(0, ['error', 'oops'], result)

    @pytest.mark.parametrize(('options', 'error_message'), [
        (['-a', '{"foo":15}'], 'foo is not a network field'),
        (['--schedule-time', '150', '-a', '{"network":"192.168.1.0/24"}'], 'schedule_time must be a positive'
                                                                           ' integer representing a FUTURE TIME')
    ])
    def test_command_raises_error_error_when_other_intern_errors_happened(self, runner, resource_name, options,
                                                                          error_message):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'update', '-o', 'foo'] + options)

        assert_in_output(2, error_message, result)


class TestDeleteCommand:
    def test_command_prints_correct_output(self, runner, responses, url, resource_name, cud_options):
        object_ref = 'delete_ref'
        responses.add(responses.DELETE, f'{url}/{object_ref}', json=object_ref, status=200)
        result = runner.invoke(cli, ['object', '-n', resource_name, 'delete', '-o', object_ref] + cud_options)

        assert 0 == result.exit_code
        assert_in_output(0, f'{json.dumps(object_ref)}\n', result)

    def test_command_prints_error_if_response_status_code_greater_or_equal_than_400(self, runner, responses, url,
                                                                                    resource_name):
        object_ref = 'delete_ref'
        responses.add(responses.DELETE, f'{url}/{object_ref}', json={'error': 'oops'}, status=400)
        result = runner.invoke(cli, ['object', '-n', resource_name, 'delete', '-o', object_ref])

        assert_list_items(0, ['error', 'oops'], result)

    def test_command_raises_error_when_other_intern_errors_happened(self, runner, resource_name):
        result = runner.invoke(cli, ['object', '-n', resource_name, 'delete', '-o', 'foo', '--schedule-time', '450'])

        assert_in_output(2, 'schedule_time must be a positive integer representing a FUTURE TIME', result)
