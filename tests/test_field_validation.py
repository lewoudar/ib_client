"""Tests resource_name methods which helps to validate user queries"""

import pytest
import requests

from infoblox_client.exceptions import BadParameterError, FieldNotFoundError, SearchOnlyFieldError
from infoblox_client.resource import Resource


@pytest.fixture(scope='module')
def network_schema():
    return {
        "cloud_additional_restrictions": [],
        "fields": [
            {
                "doc": "Authority for the DHCP network.",
                "is_array": False,
                "name": "authority",
                "overridden_by": "use_authority",
                "standard_field": False,
                "supports": "rwu",
                "type": [
                    "bool"
                ]
            },
            {
                "doc": "When specified in searches, the returned network is the smallest network that"
                       " contains this IPv4 Address.",
                "is_array": False,
                "standard_field": False,
                "name": "contains_address",
                "supports": "s",
                "type": [
                    "string"
                ]
            }
        ],
        "restrictions": [],
        "schema_version": "2",
        "type": "network",
        "version": "2.9",
        "wapi_primitive": "object"
    }


# To understand tests, translate class names in kebab-case to know the targeted method tested.


class TestValidateReturnFields:
    # this is done to avoid using directly protected methods. My editor Pycharm does not
    # like that :(
    class MyResource(Resource):
        def validate_return_fields(self, fields):
            self._validate_return_fields(fields)

    url = 'http://foo/wapi/v2.9'
    resource_name = 'network'

    @pytest.mark.parametrize('fields', [
        ('foo',),
        [4.0],
        [4],
    ])
    def test_method_raises_error_when_fields_type_are_incorrect(self, network_schema, responses, fields):
        responses.add(responses.GET, f'{self.url}/{self.resource_name}', json=network_schema, status=200)
        resource = self.MyResource(requests.Session(), self.url, 'network')

        with pytest.raises(BadParameterError) as exc_info:
            resource.validate_return_fields(fields)

        assert 'fields must be a list of strings' in str(exc_info.value)

    @pytest.mark.parametrize('field', ['foo', 'bar', 'potatoes'])
    def test_method_raises_error_when_fields_are_unknown(self, network_schema, responses, field):
        responses.add(responses.GET, f'{self.url}/{self.resource_name}', json=network_schema, status=200)
        resource = self.MyResource(requests.Session(), self.url, 'network')

        with pytest.raises(FieldNotFoundError):
            resource.validate_return_fields([field])

    def test_method_raises_error_when_fields_are_search_only(self, network_schema, responses):
        search_only_field = 'contains_address'
        responses.add(responses.GET, f'{self.url}/{self.resource_name}', json=network_schema, status=200)
        resource = self.MyResource(requests.Session(), self.url, 'network')

        with pytest.raises(SearchOnlyFieldError) as exc_info:
            resource.validate_return_fields([search_only_field])

        assert f'{search_only_field} is a search only field. It cannot be returned' == str(exc_info.value)

    @pytest.mark.parametrize('fields', [
        ['authority'],
        ['authority', 'extattrs']
    ])
    def test_method_does_not_raise_error_when_giving_correct_argument(self, network_schema, responses, fields):
        responses.add(responses.GET, f'{self.url}/{self.resource_name}', json=network_schema, status=200)
        resource = self.MyResource(requests.Session(), self.url, 'network')

        try:
            resource.validate_return_fields(fields)
        except BadParameterError:
            pytest.fail('_validate_return_fields raise an error when giving correct arguments')
