"""Tests modify Resource method"""
import json
from urllib.parse import urlparse, parse_qsl

import pytest

from infoblox.exceptions import MandatoryFieldError, FieldNotFoundError, FieldError, BadParameterError, HttpError


def test_method_raises_error_when_object_ref_is_missing(resource):
    with pytest.raises(MandatoryFieldError) as exc_info:
        resource.update()

    assert 'object_ref is missing' == str(exc_info.value)


@pytest.mark.parametrize('parameters', [
    {'foo': 1},
    {'bar': 1}
])
def test_method_raises_error_when_field_is_unknown(resource, parameters, resource_name):
    with pytest.raises(FieldNotFoundError) as exc_info:
        resource.update(object_ref='ref', **parameters)

    assert f'is not a {resource_name} field' in str(exc_info.value)


def test_method_raises_error_when_field_does_not_supports_update(resource):
    with pytest.raises(FieldError) as exc_info:
        resource.update(object_ref='ref', dhcp_utilization_status='LOW')

    assert f"dhcp_utilization_status cannot be updated, operations supported by" \
           f" this field are: ['read']" == str(exc_info.value)


@pytest.mark.parametrize('parameters', [
    {'authority': 'foo'},
    {'comment': 2}
])
def test_method_raises_error_when_field_value_is_incorrect(resource, parameters):
    with pytest.raises(FieldError) as exc_info:
        resource.update(object_ref='ref', **parameters)

    assert 'must have one of the following types' in str(exc_info.value)


@pytest.mark.parametrize('parameters', [
    {'schedule_now': 'foo'},
    {'approval_ticket_number': 'foo'}
])
def test_method_raises_error_when_approval_or_schedule_query_parameters_are_incorrect(resource, parameters):
    with pytest.raises(BadParameterError):
        resource.update(object_ref='ref', **parameters)


@pytest.mark.parametrize('parameters', [
    {'return_fields': 2},
    {'return_fields_plus': 2}
])
def test_method_raises_error_when_return_fields_are_incorrect(resource, parameters):
    with pytest.raises(BadParameterError) as exc_info:
        resource.update(object_ref='ref', **parameters)

    assert 'fields must be a list of strings' in str(exc_info.value)


def test_method_raises_error_when_http_status_code_greater_or_equal_than_400(responses, url, resource):
    object_ref = 'ref'
    responses.add(responses.PUT, f'{url}/{object_ref}', json={'error': 'oops'}, status=400)
    with pytest.raises(HttpError):
        resource.update(object_ref)


def test_method_returns_correct_data_without_return_fields(responses, url, resource):
    object_ref = 'object_ref'
    responses.add(responses.PUT, f'{url}/{object_ref}', json=object_ref, status=200)

    assert object_ref == resource.update(object_ref=object_ref, comment='my comment')


@pytest.mark.parametrize(('parameters', 'expected_keys'), [
    ({'return_fields': ['comment', 'authority']}, ['_ref', 'comment', 'authority']),
    ({'return_fields_plus': ['authority', 'dhcp_utilization_status']}, ['_ref', 'authority', 'dhcp_utilization_status'])
])
def test_method_returns_correct_data_with_return_fields(responses, url, resource, parameters, expected_keys):
    object_ref = 'update-ref'

    def request_callback(request):
        payload = {'_ref': object_ref}
        url_parts = urlparse(request.url)
        query_dict = dict(parse_qsl(url_parts.query))
        if '_return_fields+' in query_dict:
            # we don't care about field values, just field presence matters
            for field in query_dict['_return_fields+'].split(','):
                payload[field] = 'foo'
        elif '_return_fields' in query_dict:
            for field in query_dict['_return_fields'].split(','):
                payload[field] = 'foo'
        return 200, {}, json.dumps(payload)

    responses.add_callback(responses.PUT, f'{url}/{object_ref}', callback=request_callback,
                           content_type='application/json')

    response: dict = resource.update(object_ref=object_ref, **parameters)
    assert sorted(expected_keys) == sorted(list(response.keys()))
