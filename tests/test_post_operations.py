"""Tests Resource methods create and func_call"""
import json

import pytest

from infoblox_client.exceptions import MandatoryCreationFieldError, BadParameterError


class TestPostMethod:
    def test_method_raises_error_when_mandatory_field_is_missing(self, resource):
        with pytest.raises(MandatoryCreationFieldError) as exc_info:
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
