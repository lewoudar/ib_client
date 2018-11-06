"""Tests Resource methods create and func_call"""
import json

import pytest

from infoblox.exceptions import MandatoryFieldError, BadParameterError, FunctionNotFoundError, \
    FieldError, HttpError


# To know which methods are tests, remove Test from class names and put it in lower case.
from tests.helpers import ResponseMock


class TestCreate:
    def test_method_raises_error_when_mandatory_field_is_missing(self, resource):
        with pytest.raises(MandatoryFieldError) as exc_info:
            resource.create()

        assert 'network field is mandatory for network creation but is missing' == str(exc_info.value)

    @pytest.mark.parametrize('field_parameter', [
        {'network': '192.168.1.0/24', 'comment': 'foo'},
        {'network': '192.168.1.0/24', 'authority': 'foo'}
    ])
    def test_method_raises_error_when_field_passed_is_not_mandatory(self, resource, field_parameter):
        with pytest.raises(BadParameterError) as exc_info:
            resource.create(**field_parameter)

        assert 'is not in mandatory create fields' in str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'schedule_now': 'foo', 'network': '192.168.1.0/24'},
        {'approval_ticket_number': 'foo', 'network': '192.168.1.0/24'}
    ])
    def test_method_raises_error_if_some_query_parameters_are_incorrect(self, resource, parameters):
        with pytest.raises(BadParameterError):
            resource.create(**parameters)

    def test_method_returns_object_reference_when_creation_is_done(self, responses, url, resource_name, resource):
        def request_callback(request):
            payload = json.loads(request.body)
            network = payload['network']
            return 201, {}, json.dumps(f'network/just-a-string:{network}')

        responses.add_callback(responses.POST, f'{url}/{resource_name}', callback=request_callback,
                               content_type='application/json')

        cidr = '192.168.1.0/24'
        assert cidr in resource.create(network=cidr)


@pytest.mark.parametrize(('field_name', 'field_type'), [
    ('num', 'input'),
    ('exclude', 'input'),
    ('ips', 'output')
])
def test_get_field_info_from_function_info_returns_correct_data(resource, field_name, field_type):
    function_info = resource.get_function_information('next_available_ip')
    function_field_info = resource.get_field_info_from_function_info(function_info, field_name, field_type)
    assert field_name == function_field_info['name']


class TestFuncCall:
    @pytest.mark.parametrize(('parameters', 'error_message'), [
        ({}, 'object_ref is missing'),
        ({'object_ref': 'my-ref'}, 'function_name is missing')
    ])
    def test_method_raises_error_when_mandatory_fields_are_missing(self, resource, parameters, error_message):
        with pytest.raises(MandatoryFieldError) as exc_info:
            resource.func_call(**parameters)

        assert error_message == str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'object_ref': 4},
        {'object_ref': 4.0},
        {'object_ref': 'my-ref', 'function_name': 4},
        {'object_ref': 'my-ref', 'function_name': 4.0}
    ])
    def test_method_raises_error_when_mandatory_fields_have_incorrect_type(self, resource, parameters):
        with pytest.raises(BadParameterError) as exc_info:
            resource.func_call(**parameters)

        assert 'must be a string' in str(exc_info.value)

    def test_method_raises_error_if_function_name_is_unknown(self, resource, resource_name):
        function_name = 'foo'
        with pytest.raises(FunctionNotFoundError) as exc_info:
            resource.func_call(object_ref='ref', function_name=function_name)

        assert f'{function_name} is an unknown function for {resource_name} object' == str(exc_info.value)

    @pytest.mark.parametrize('field_parameter', [
        {'authority': 'foo'},
        {'contains_address': 'foo'}
    ])
    def test_method_raises_error_when_input_field_function_is_not_correct(self, resource, field_parameter):
        function_name = 'next_available_ip'
        with pytest.raises(BadParameterError) as exc_info:
            resource.func_call(object_ref='ref', function_name=function_name, **field_parameter)

        assert f'is not a valid input field for {function_name} function' in str(exc_info.value)

    @pytest.mark.parametrize(('field_parameter', 'error_message'), [
        ({'num': 'foo'}, 'must have one of the following types'),
        ({'exclude': 'foo'}, 'must be a list')
    ])
    def test_method_raises_error_when_input_field_value_is_incorrect(self, resource, field_parameter, error_message):
        with pytest.raises(FieldError) as exc_info:
            resource.func_call(object_ref='ref', function_name='next_available_ip', **field_parameter)

        assert error_message in str(exc_info.value)

    def test_method_raises_error_when_http_status_code_is_greater_or_equal_than_400(self, responses, url, resource):
        object_ref = 'ref'
        responses.add(responses.POST, f'{url}/{object_ref}', json={'error': 'oops'}, status=400)
        with pytest.raises(HttpError):
            resource.func_call(object_ref=object_ref, function_name='next_available_ip', num=3)

    @pytest.mark.withoutresponses
    def test_method_is_executed_correctly_and_returns_correct_data(self, mocker, url, resource):
        object_ref = 'ref'
        function_name = 'next_available_ip'
        payload = {'num': 1}
        expected_response = {'ips': ['192.168.1.1']}
        post_mock = mocker.patch('requests.sessions.Session.post')
        post_mock.return_value = ResponseMock(expected_response, 200)

        assert expected_response == resource.func_call(object_ref, function_name, **payload)
        post_mock.assert_called_once_with(f'{url}/{object_ref}', params={'_function': function_name}, json=payload)
