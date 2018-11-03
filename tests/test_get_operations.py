from urllib.parse import urlencode

import pytest

from infoblox_client.exceptions import BadParameterError, UnknownReturnTypeError, FieldError, FieldNotFoundError, \
    SearchOnlyFieldError, HttpError


class TestProxySearchParameter:
    @pytest.mark.parametrize('proxy_search', ['foo', 'bar'])
    def test_get_method_raises_error_when_proxy_search_is_incorrect(self, resource, proxy_search):
        with pytest.raises(BadParameterError) as exc_info:
            resource.get(proxy_search=proxy_search)

        assert 'proxy_search must be in' in str(exc_info.value)

    @pytest.mark.parametrize('proxy_search', ['GM', 'local', 'Gm', 'locAl'])
    def test_get_method_does_not_raises_error_when_proxy_search_is_correct(self, resource, proxy_search):
        try:
            resource.get(proxy_search=proxy_search)
        except BadParameterError:
            pytest.fail(f'get method unexpectedly fails with proxy_search = {proxy_search}')


class TestGetMethodRaisesDifferentParameterErrors:
    @pytest.mark.parametrize('return_type', ['soap', 'application/csv'])
    def test_get_method_raises_error_when_return_type_is_incorrect(self, resource, return_type):
        with pytest.raises(UnknownReturnTypeError):
            resource.get(return_type=return_type)

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
    ({'return_fields': ['authority', 'email_list']}, {'_return_fields': 'authority,email_list'}),
    ({'return_fields_plus': ['authority', 'email_list']}, {'_return_fields+': 'authority,email_list'}),
    ({'return_fields': ['authority'], 'return_fields_plus': ['email_list']}, {'_return_fields': 'authority'}),
    ({'return_fields_plus': ['email_list', 'comment']}, {'_return_fields+': 'email_list'}),
    ({'proxy_search': 'LOCAL'}, {'_proxy_search': 'LOCAL'})
])
def test_get_method_is_called_with_correct_arguments(responses, url, resource_name, resource, parameters, query_dict):
    resource.get(**parameters)
    params = {'_return_type': 'json'}
    params = {**params, **query_dict}
    # it is the second call to the url, because the first loads the schema
    assert responses.calls[1].request.url == f'{url}/{resource_name}?{urlencode(params)}'


def test_get_method_returns_json_when_infoblox_returns_json(responses, url, resource_name, resource):
    payload = {'data': 'infoblox'}
    responses.replace(responses.GET, f'{url}/{resource_name}', json=payload, status=200)
    assert payload == resource.get()
