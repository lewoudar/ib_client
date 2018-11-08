import pytest

from infoblox.exceptions import MandatoryFieldError, BadParameterError, HttpError


def test_method_raises_error_when_object_ref_is_missing(resource):
    with pytest.raises(MandatoryFieldError) as exc_info:
        resource.delete()

    assert 'object_ref is missing' == str(exc_info.value)


@pytest.mark.parametrize('parameters', [
    {'schedule_now': 'foo'},
    {'approval_ticket_number': 'foo'}
])
def test_method_raises_error_when_approval_or_schedule_query_parameters_are_incorrect(resource, parameters):
    with pytest.raises(BadParameterError):
        resource.delete(object_ref='ref', **parameters)


def test_method_raises_error_when_http_status_code_greater_or_equal_than_400(responses, url, resource):
    object_ref = 'ref'
    responses.add(responses.DELETE, f'{url}/{object_ref}', json={'error': 'oops'}, status=400)
    with pytest.raises(HttpError):
        resource.delete(object_ref)


def test_method_returns_object_ref_when_infoblox_deletes_object(responses, url, resource):
    object_ref = 'ref'
    responses.add(responses.DELETE, f'{url}/{object_ref}', json=object_ref, status=200)

    assert object_ref == resource.delete(object_ref)
