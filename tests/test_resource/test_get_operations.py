from urllib.parse import urlencode

import pytest

from infoblox.exceptions import BadParameterError, FieldError, FieldNotFoundError, \
    SearchOnlyFieldError, HttpError


class TestGetMethodRaisesDifferentParameterErrors:
    @pytest.mark.parametrize('proxy_search', [4, 'foo', 'bar'])
    def test_get_method_raises_error_when_proxy_search_is_incorrect(self, resource, proxy_search):
        with pytest.raises(BadParameterError):
            resource.get(proxy_search=proxy_search)

    @pytest.mark.parametrize(('parameters', 'exception'), [
        ({'params': {'contains_address!': '10.0.0.4'}}, FieldError),
        ({'params': {'foo': '10.0.0.4'}}, FieldNotFoundError),
        ({'params': {'authority': 'foo'}}, FieldError)
    ])
    def test_get_method_raises_error_when_params_parameter_is_incorrect(self, resource, parameters, exception):
        with pytest.raises(exception):
            resource.get(**parameters)

    @pytest.mark.parametrize(('parameters', 'exception'), [
        ({'return_fields': [4.0, 4]}, BadParameterError),
        ({'return_fields_plus': [4.0, 4]}, BadParameterError),
        ({'return_fields': ['contains_address']}, SearchOnlyFieldError),
        ({'return_fields_plus': ['contains_address']}, SearchOnlyFieldError),
        ({'return_fields': ['foo']}, FieldNotFoundError),
        ({'return_fields_plus': ['foo']}, FieldNotFoundError),
    ])
    def test_get_method_raises_error_when_returned_fields_are_incorrect(self, resource, parameters, exception):
        with pytest.raises(exception):
            resource.get(**parameters)


@pytest.mark.parametrize('status_code', [400, 500])
def test_get_method_raises_error_when_status_code_greater_or_equal_than_400(responses, url, resource_name, resource,
                                                                            status_code):
    responses.replace(responses.GET, f'{url}/{resource_name}', json={'error': 'oops'}, status=status_code)
    with pytest.raises(HttpError) as exc_info:
        resource.get()

    assert status_code == exc_info.value.status_code


@pytest.mark.parametrize(('parameters', 'query_dict'), [
    ({}, {}),
    ({'params': {'comment': 'foo'}}, {'comment': 'foo'}),
    ({'return_fields': ['authority', 'email_list']}, {'_return_fields': 'authority,email_list'}),
    ({'return_fields_plus': ['authority', 'email_list']}, {'_return_fields+': 'authority,email_list'}),
    ({'return_fields': ['authority'], 'return_fields_plus': ['email_list']}, {'_return_fields': 'authority'}),
    ({'return_fields_plus': ['email_list', 'comment']}, {'_return_fields+': 'email_list'}),
    ({'proxy_search': 'LOCAL'}, {'_proxy_search': 'LOCAL'})
])
def test_get_method_is_called_with_correct_arguments(responses, url, resource_name, resource, parameters, query_dict):
    resource.get(**parameters)
    resolved_url = f'{url}/{resource_name}'
    if query_dict:
        resolved_url = f'{resolved_url}?{urlencode(query_dict)}'
    # it is the second call to the url, because the first loads the schema
    assert responses.calls[1].request.url == resolved_url


def test_get_method_returns_correct_data(responses, url, resource_name, resource):
    payload = {'network': '10.1.0.0/16', 'networkview': 'default'}
    responses.replace(responses.GET, f'{url}/{resource_name}', json=payload, status=200)
    assert payload == resource.get()


class TestGetObjectByReference:
    @pytest.mark.parametrize('object_ref', [4, 4.0])
    def test_get_method_raises_error_when_object_ref_is_incorrect(self, resource, object_ref):
        with pytest.raises(BadParameterError) as exc_info:
            resource.get(object_ref=object_ref)

        assert f'object_ref must be a string but you provide {object_ref}' == str(exc_info.value)

    def test_get_method_does_not_use_params_in_query_string_if_object_ref_is_present(self, responses, url, resource):
        object_ref = 'object_ref'
        parameters = {'params': {'comment': 'foo'}, 'object_ref': object_ref}
        object_url = f'{url}/{object_ref}'
        responses.add(responses.GET, object_url, json={'network': '10.1.0.0/16'}, status=200)

        resource.get(**parameters)
        assert responses.calls[1].request.url == f'{object_url}'

    def test_get_method_returns_correct_data(self, responses, url, resource):
        payload = {'network': '10.1.0.0/16', 'networkview': 'default'}
        object_ref = 'object_ref'
        responses.add(responses.GET, f'{url}/{object_ref}', json=payload, status=200)

        assert payload == resource.get(object_ref=object_ref)


# we test the method get_multiple
class TestGetMultiple:
    def test_method_calls_process_get_parameters(self, mocker, responses, url, resource_name, resource):
        process_mock = mocker.patch('infoblox.resource.Resource._process_get_parameters')
        process_mock.return_value = {}
        payload = {'result': [{'network': '192.168.1.24/0'}]}
        responses.replace(responses.GET, f'{url}/{resource_name}', json=payload, status=200)
        list(resource.get_multiple())

        process_mock.assert_called_once_with(object_ref=None, params=None, return_fields=None, return_fields_plus=None,
                                             proxy_search=None)

    def test_method_raises_error_when_status_code_greater_or_equal_than_400(self, responses, url, resource_name,
                                                                            resource):
        responses.replace(responses.GET, f'{url}/{resource_name}', json={'error': 'oops'}, status=400)
        with pytest.raises(HttpError):
            list(resource.get_multiple())

    def test_method_returns_correct_data_with_next_page_id(self, responses, url, resource_name, resource):
        network_objects = [{'network': f'192.168.{i}.0/24', 'networkview': 'default'} for i in range(1, 7)]
        payload_1 = {
            'next_page_id': 'ir45',
            'result': network_objects[:2]
        }
        payload_2 = {
            'result': network_objects[2:]
        }
        responses.replace(responses.GET, f'{url}/{resource_name}', json=payload_1, status=200)

        counter = 0
        for item in resource.get_multiple():
            if counter == 0:
                responses.replace(responses.GET, f'{url}/{resource_name}', json=payload_2, status=200)
            assert network_objects[counter] == item
            counter += 1

    def test_method_returns_correct_data_without_next_page_id(self, responses, url, resource_name, resource):
        network_objects = [{'network': f'192.168.{i}.0/24', 'networkview': 'default'} for i in range(1, 3)]
        payload = {'result': network_objects}
        responses.replace(responses.GET, f'{url}/{resource_name}', json=payload, status=200)

        counter = 0
        for item in resource.get_multiple():
            assert network_objects[counter] == item
            counter += 1


class TestCount:
    def test_method_calls_get_multiple(self, mocker, resource):
        get_multiple_mock = mocker.patch('infoblox.resource.Resource.get_multiple')
        get_multiple_mock.return_value = []
        resource.count()

        get_multiple_mock.assert_called_once_with(None, proxy_search=None)

    @pytest.mark.parametrize(('networks', 'expected_value'), [
        ([{'network': f'192.168.{i}.0/24'} for i in range(1, 5)], 4),
        ([], 0),
    ])
    def test_method_returns_correct_value(self, responses, url, resource_name, resource, networks,
                                          expected_value):
        responses.replace(responses.GET, f'{url}/{resource_name}', json={'result': networks}, status=200)

        assert expected_value == resource.count()
