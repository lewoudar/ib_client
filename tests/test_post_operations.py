"""Tests Resource methods create and func_call"""
import json
from urllib.parse import urlparse, parse_qsl

import pytest

from infoblox.exceptions import MandatoryFieldError, BadParameterError, FunctionNotFoundError, \
    FieldError, HttpError, FieldNotFoundError
from tests.helpers import ResponseMock

# To know which methods are tests, remove Test from class names and put it in lower case.


class TestCreate:
    def test_method_raises_error_when_mandatory_field_is_missing(self, resource):
        with pytest.raises(MandatoryFieldError) as exc_info:
            resource.create()

        assert 'network field is mandatory for network creation but is missing' == str(exc_info.value)

    @pytest.mark.parametrize('field_parameters', [
        {'network': '192.168.1.0/24', 'foo': 'foo'},
        {'network': '192.168.1.0/24', 'bar': 'foo'}
    ])
    def test_method_raises_error_when_field_passed_is_unknown(self, resource, resource_name, field_parameters):
        with pytest.raises(FieldNotFoundError) as exc_info:
            resource.create(**field_parameters)

            assert f'is not a {resource_name} field' in str(exc_info.value)

    def test_method_raises_error_when_field_does_not_supports_write(self, resource):
        with pytest.raises(FieldError) as exc_info:
            resource.create(network='192.168.1.0/24', dhcp_utilization_status='FULL')

        assert "dhcp_utilization_status cannot be written, operations supported by" \
               " this field are: ['read']" == str(exc_info.value)

    @pytest.mark.parametrize('field_parameters', [
        {'network': '192.168.1.0/24', 'comment': 2},
        {'network': 2}
    ])
    def test_method_raises_error_when_field_value_is_incorrect(self, resource, field_parameters):
        with pytest.raises(FieldError) as exc_info:
            resource.create(**field_parameters)

        assert 'must have one of the following types' in str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'schedule_now': 'foo', 'network': '192.168.1.0/24'},
        {'approval_ticket_number': 'foo', 'network': '192.168.1.0/24'}
    ])
    def test_method_raises_error_when_approval_or_schedule_parameters_are_incorrect(self, resource, parameters):
        with pytest.raises(BadParameterError):
            resource.create(**parameters)

    @pytest.mark.parametrize('parameters', [
        {'return_fields': 2, 'network': '192.168.1.0/24'},
        {'return_fields_plus': 2, 'network': '192.168.1.0/24'}
    ])
    def test_method_raises_error_when_return_fields_are_incorrect(self, resource, parameters):
        with pytest.raises(BadParameterError):
            resource.create(**parameters)

    def test_method_raises_error_when_http_status_code_greater_or_equal_than_400(self, responses, url, resource_name,
                                                                                 resource):
        responses.add(responses.POST, f'{url}/{resource_name}', json={'error': 'oops'}, status=400)

        with pytest.raises(HttpError):
            resource.create(network='192.168.1.0/24')

    def test_method_returns_object_reference_when_creation_is_done_without_return_fields(self, responses, url,
                                                                                         resource_name, resource):
        def request_callback(request):
            payload = json.loads(request.body)
            network = payload['network']
            return 201, {}, json.dumps(f'network/just-a-string:{network}')

        responses.add_callback(responses.POST, f'{url}/{resource_name}', callback=request_callback,
                               content_type='application/json')

        cidr = '192.168.1.0/24'
        assert cidr in resource.create(network=cidr)

    @pytest.mark.parametrize(('parameters', 'expected_keys'), [
        ({'return_fields': ['comment', 'authority']}, ['_ref', 'comment', 'authority']),
        ({'return_fields_plus': ['authority', 'dhcp_utilization_status']},
         ['_ref', 'authority', 'dhcp_utilization_status'])
    ])
    def test_method_returns_correct_data_when_creation_is_done_with_return_fields(self, responses, url, resource_name,
                                                                                  resource, parameters, expected_keys):
        def request_callback(request):
            request_payload = json.loads(request.body)
            payload = {'_ref': f"network/just-a-string:{request_payload['network']}"}
            url_parts = urlparse(request.url)
            query_dict = dict(parse_qsl(url_parts.query))
            if '_return_fields+' in query_dict:
                for field in query_dict['_return_fields+'].split(','):
                    payload[field] = 'foo'
            elif '_return_fields' in query_dict:
                for field in query_dict['_return_fields'].split(','):
                    payload[field] = 'foo'
            return 201, {}, json.dumps(payload)

        responses.add_callback(responses.POST, f'{url}/{resource_name}', callback=request_callback,
                               content_type='application/json')

        cidr = '192.168.1.0/24'
        response: dict = resource.create(network=cidr, **parameters)
        assert sorted(expected_keys) == sorted(list(response.keys()))
        assert cidr in response['_ref']


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
