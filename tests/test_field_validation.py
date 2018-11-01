"""Tests resource_name methods which helps to validate user queries"""

import pytest
import requests

from infoblox_client.exceptions import BadParameterError, FieldNotFoundError, SearchOnlyFieldError, \
    UnknownReturnTypeError, FieldError, FunctionNotFoundError
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
                "doc": "A string describing the utilization level of the network.",
                "enum_values": [
                    "FULL",
                    "HIGH",
                    "LOW",
                    "NORMAL"
                ],
                "is_array": False,
                "name": "dhcp_utilization_status",
                "standard_field": False,
                "supports": "r",
                "type": [
                    "enum"
                ]
            },
            {
                "doc": "The e-mail lists to which the appliance sends DHCP threshold alarm e-mail messages.",
                "is_array": True,
                "name": "email_list",
                "overridden_by": "use_email_list",
                "standard_field": False,
                "supports": "rwu",
                "type": [
                    "string"
                ]
            },
            {
                "doc": "An integer that specifies the period of time (in seconds) that frees and backs up leases"
                       " remained in the database before they are automatically deleted. To disable lease scavenging,"
                       " set the parameter to -1. The minimum positive value must be greater "
                       "than 86400 seconds (1 day).",
                "is_array": False,
                "name": "lease_scavenge_time",
                "overridden_by": "use_lease_scavenge_time",
                "standard_field": False,
                "supports": "rwu",
                "type": [
                    "int"
                ]
            },
            {
                "doc": "An array of DHCP option dhcpoption structs that lists the DHCP options"
                       " associated with the object.",
                "is_array": True,
                "name": "options",
                "overridden_by": "use_options",
                "schema": {
                    "fields": [
                        {
                            "doc": "Name of the DHCP option.",
                            "is_array": False,
                            "name": "name",
                            "supports": "rwu",
                            "type": [
                                "string"
                            ]
                        },
                        {
                            "doc": "The code of the DHCP option.",
                            "is_array": False,
                            "name": "num",
                            "supports": "rwu",
                            "type": [
                                "uint"
                            ]
                        },
                        {
                            "doc": "The name of the space this DHCP option is associated to.",
                            "is_array": False,
                            "name": "vendor_class",
                            "supports": "rwu",
                            "type": [
                                "string"
                            ]
                        },
                        {
                            "doc": "Value of the DHCP option",
                            "is_array": False,
                            "name": "value",
                            "supports": "rwu",
                            "type": [
                                "string"
                            ]
                        },
                        {
                            "doc": "Only applies to special options that are displayed separately from other options"
                                   " and have a use flag. These options are: * routers * router-templates *"
                                   " domain-name-servers * domain-name * broadcast-address * broadcast-address-offset *"
                                   " dhcp-lease-time * dhcp6.name-servers",
                            "is_array": False,
                            "name": "use_option",
                            "supports": "rwu",
                            "type": [
                                "bool"
                            ]
                        }
                    ]
                },
                "standard_field": False,
                "supports": "rwu",
                "type": [
                    "dhcpoption"
                ],
                "wapi_primitive": "struct"
            },
            {
                "doc": "When specified in searches, the returned network is the smallest network that"
                       " contains this IPv4 Address.",
                "is_array": False,
                "standard_field": False,
                "name": "contains_address",
                "searchable_by": "=",
                "supports": "s",
                "type": [
                    "string"
                ]
            },
            {
                "doc": "The DHCP Network Cisco ISE subscribe settings.",
                "is_array": False,
                "name": "subscribe_settings",
                "overridden_by": "use_subscribe_settings",
                "schema": {
                    "fields": [
                        {
                            "doc": "The list of Cisco ISE attributes allowed for subscription.",
                            "enum_values": [
                                "DOMAINNAME",
                                "ENDPOINT_PROFILE",
                                "SECURITY_GROUP",
                                "SESSION_STATE",
                                "SSID",
                                "USERNAME",
                                "VLAN"
                            ],
                            "is_array": True,
                            "name": "enabled_attributes",
                            "supports": "rwu",
                            "type": [
                                "enum"
                            ]
                        },
                        {
                            "doc": "The list of NIOS extensible attributes to Cisco ISE attributes mappings.",
                            "is_array": True,
                            "name": "mapped_ea_attributes",
                            "schema": {
                                "fields": [
                                    {
                                        "doc": "The Cisco ISE attribute name that is enabled for publishsing from a Cisco ISE endpoint.",
                                        "enum_values": [
                                            "ACCOUNT_SESSION_ID",
                                            "AUDIT_SESSION_ID",
                                            "EPS_STATUS",
                                            "IP_ADDRESS",
                                            "MAC",
                                            "NAS_IP_ADDRESS",
                                            "NAS_PORT_ID",
                                            "POSTURE_STATUS",
                                            "POSTURE_TIMESTAMP"
                                        ],
                                        "is_array": False,
                                        "name": "name",
                                        "supports": "rwu",
                                        "type": [
                                            "enum"
                                        ]
                                    },
                                    {
                                        "doc": "The name of the extensible attribute definition object the Cisco ISE"
                                               " attribute that is enabled for subscription is mapped on.",
                                        "is_array": False,
                                        "name": "mapped_ea",
                                        "supports": "rwu",
                                        "type": [
                                            "string"
                                        ]
                                    }
                                ]
                            },
                            "supports": "rwu",
                            "type": [
                                "ciscoise:eaassociation"
                            ],
                            "wapi_primitive": "struct"
                        }
                    ]
                },
                "standard_field": False,
                "supports": "rwu",
                "type": [
                    "ciscoise:subscribesetting"
                ],
                "wapi_primitive": "struct"
            },
            {
                "doc": "This function reduces the subnet masks of a network by joining all networks that fall under it."
                       " All the ranges and fixed addresses of the original networks are reparented to the new joined"
                       " network. Any network containers that fall inside the bounds of the joined network are removed",
                "is_array": False,
                "name": "expand_network",
                "schema": {
                    "input_fields": [
                        {
                            "doc": "The netmask of the networks after the expand operation.",
                            "is_array": False,
                            "name": "prefix",
                            "supports": "w",
                            "type": [
                                "uint"
                            ]
                        },
                        {
                            "doc": "Determines whether or not to automatically create reverse-mapping zones.",
                            "is_array": False,
                            "name": "auto_create_reversezone",
                            "supports": "w",
                            "type": [
                                "bool"
                            ]
                        },
                        {
                            "doc": "The option to be applied on deleted networks with existing extensible attribute.",
                            "enum_values": [
                                "RETAIN",
                                "REMOVE"
                            ],
                            "is_array": False,
                            "name": "option_delete_ea",
                            "supports": "w",
                            "type": [
                                "enum"
                            ]
                        }
                    ],
                    "output_fields": [
                        {
                            "doc": "The reference to the resulting network that is created after the expand operation.",
                            "is_array": False,
                            "name": "network",
                            "supports": "r",
                            "type": [
                                "string"
                            ]
                        }
                    ]
                },
                "standard_field": False,
                "supports": "rwu",
                "type": [
                    "expandnetwork"
                ],
                "wapi_primitive": "funccall"
            }
        ],
        "restrictions": [],
        "schema_version": "2",
        "type": "network",
        "version": "2.9",
        "wapi_primitive": "object"
    }


# this is done to avoid using directly protected methods. My editor Pycharm does not
# like that :(
class MyResource(Resource):
    def get_field_support_information(self, support_string):
        return self._get_field_support_information(support_string)

    def get_field_searchable_information(self, search_string):
        return self._get_field_searchable_information(search_string)

    def validate_return_fields(self, fields):
        self._validate_return_fields(fields)

    def validate_return_type(self, return_type):
        self._validate_return_type(return_type)

    def get_type_mapping(self, field_types):
        return self._get_type_mapping(field_types)

    def check_field_value(self, name, value, field_info=None):
        self._check_field_value(name, value, field_info)

    def validate_params(self, params):
        self._validate_params(params)


@pytest.fixture
def resource(responses, network_schema):
    url = 'http://foo/wapi/v2.9'
    resource_name = 'network'
    responses.add(responses.GET, f'{url}/{resource_name}', json=network_schema, status=200)
    return MyResource(requests.Session(), url, resource_name)


# To understand tests, translate class names in kebab-case to know the targeted method tested.

@pytest.mark.parametrize(('field_name', 'field_structure'), [
    ('authority', {
        "doc": "Authority for the DHCP network.",
        "is_array": False,
        "name": "authority",
        "overridden_by": "use_authority",
        "standard_field": False,
        "supports": ['read', 'write', 'update'],
        "type": [
            "bool"
        ],
        "searchable_by": []
    }),
    ('dhcp_utilization_status', {
        "doc": "A string describing the utilization level of the network.",
        "enum_values": [
            "FULL",
            "HIGH",
            "LOW",
            "NORMAL"
        ],
        "is_array": False,
        "name": "dhcp_utilization_status",
        "standard_field": False,
        "supports": ['read'],
        "type": [
            "enum"
        ],
        "searchable_by": []
    }),
    ('options', {
        "doc": "An array of DHCP option dhcpoption structs that lists the DHCP options"
               " associated with the object.",
        "is_array": True,
        "name": "options",
        "overridden_by": "use_options",
        "schema": {
            "fields": [
                {
                    "doc": "Name of the DHCP option.",
                    "is_array": False,
                    "name": "name",
                    "supports": ['read', 'write', 'update'],
                    "type": [
                        "string"
                    ],
                    "searchable_by": []
                },
                {
                    "doc": "The code of the DHCP option.",
                    "is_array": False,
                    "name": "num",
                    "supports": ['read', 'write', 'update'],
                    "type": [
                        "uint"
                    ],
                    "searchable_by": []
                },
                {
                    "doc": "The name of the space this DHCP option is associated to.",
                    "is_array": False,
                    "name": "vendor_class",
                    "supports": ['read', 'write', 'update'],
                    "type": [
                        "string"
                    ],
                    "searchable_by": []
                },
                {
                    "doc": "Value of the DHCP option",
                    "is_array": False,
                    "name": "value",
                    "supports": ['read', 'write', 'update'],
                    "type": [
                        "string"
                    ],
                    "searchable_by": []
                },
                {
                    "doc": "Only applies to special options that are displayed separately from other options"
                           " and have a use flag. These options are: * routers * router-templates *"
                           " domain-name-servers * domain-name * broadcast-address * broadcast-address-offset *"
                           " dhcp-lease-time * dhcp6.name-servers",
                    "is_array": False,
                    "name": "use_option",
                    "supports": ['read', 'write', 'update'],
                    "type": [
                        "bool"
                    ],
                    "searchable_by": []
                }
            ]
        },
        "standard_field": False,
        "supports": ['read', 'write', 'update'],
        "type": [
            "dhcpoption"
        ],
        "wapi_primitive": "struct"
    },)
])
def test_get_field_information_returns_correct_info(resource, field_name, field_structure):
    assert field_structure == resource.get_field_information(field_name)


class TestGetFunctionInformation:
    def test_method_returns_correct_information(self, resource):
        field_structure = {
            "doc": "This function reduces the subnet masks of a network by joining all networks that fall under it."
                   " All the ranges and fixed addresses of the original networks are reparented to the new joined"
                   " network. Any network containers that fall inside the bounds of the joined network are removed",
            "is_array": False,
            "name": "expand_network",
            "schema": {
                "input_fields": [
                    {
                        "doc": "The netmask of the networks after the expand operation.",
                        "is_array": False,
                        "name": "prefix",
                        "supports": ['write'],
                        "type": [
                            "uint"
                        ],
                        "searchable_by": []
                    },
                    {
                        "doc": "Determines whether or not to automatically create reverse-mapping zones.",
                        "is_array": False,
                        "name": "auto_create_reversezone",
                        "supports": ['write'],
                        "type": [
                            "bool"
                        ],
                        "searchable_by": []
                    },
                    {
                        "doc": "The option to be applied on deleted networks with existing extensible attribute.",
                        "enum_values": [
                            "RETAIN",
                            "REMOVE"
                        ],
                        "is_array": False,
                        "name": "option_delete_ea",
                        "supports": ['write'],
                        "type": [
                            "enum"
                        ],
                        "searchable_by": []
                    }
                ],
                "output_fields": [
                    {
                        "doc": "The reference to the resulting network that is created after the expand operation.",
                        "is_array": False,
                        "name": "network",
                        "supports": ['read'],
                        "type": [
                            "string"
                        ],
                        "searchable_by": []
                    }
                ]
            },
            "standard_field": False,
            "supports": ['read', 'write', 'update'],
            "type": [
                "expandnetwork"
            ],
            "wapi_primitive": "funccall"
        }
        assert field_structure == resource.get_function_information('expand_network')

    @pytest.mark.parametrize('func', ['foo', 'bar'])
    def test_method_raises_error_for_unknown_function(self, resource, func):
        with pytest.raises(FunctionNotFoundError):
            resource.get_function_information(func)


@pytest.mark.parametrize(('supports', 'expected_list'), [
    ('', []),
    ('wu', ['write', 'update']),
    ('sr', ['search', 'read']),
    ('srwu', ['search', 'read', 'write', 'update']),
    ('rf', ['read'])
])
def test_get_field_support_information_returns_correct_info(resource, supports, expected_list):
    assert expected_list == resource.get_field_support_information(supports)


@pytest.mark.parametrize(('search_string', 'expected_list'), [
    ('!=', ['!', '=']),
    ('', [])
])
def test_get_field_searchable_information_returns_correct_info(resource, search_string, expected_list):
    assert expected_list == resource.get_field_searchable_information(search_string)


class TestValidateReturnFields:

    @pytest.mark.parametrize('fields', [
        ('foo',),
        [4.0],
        [4],
    ])
    def test_method_raises_error_when_fields_type_are_incorrect(self, resource, fields):
        with pytest.raises(BadParameterError) as exc_info:
            resource.validate_return_fields(fields)

        assert 'fields must be a list of strings' in str(exc_info.value)

    @pytest.mark.parametrize('field', ['foo', 'bar', 'potatoes'])
    def test_method_raises_error_when_fields_are_unknown(self, resource, field):
        with pytest.raises(FieldNotFoundError):
            resource.validate_return_fields([field])

    def test_method_raises_error_when_fields_are_search_only(self, resource):
        search_only_field = 'contains_address'

        with pytest.raises(SearchOnlyFieldError) as exc_info:
            resource.validate_return_fields([search_only_field])

        assert f'{search_only_field} is a search only field. It cannot be returned' == str(exc_info.value)

    @pytest.mark.parametrize('fields', [
        ['authority'],
        ['authority', 'extattrs', 'foo.bar']
    ])
    def test_method_does_not_raise_error_when_giving_correct_argument(self, resource, fields):
        try:
            resource.validate_return_fields(fields)
        except BadParameterError:
            pytest.fail('_validate_return_fields raise an error when giving correct arguments')


class TestValidateReturnType:

    @pytest.mark.parametrize('return_type', ['soap', 'application/csv'])
    def test_method_raises_error_when_return_type_is_incorrect(self, resource, return_type):
        with pytest.raises(UnknownReturnTypeError) as exc_info:
            resource.validate_return_type(return_type)

        assert f'{return_type} is not a valid return type' in str(exc_info.value)

    @pytest.mark.parametrize('return_type', ['json', 'json-pretty', 'xml', 'xml-pretty'])
    def test_method_does_not_raise_error_when_return_type_is_valid(self, resource, return_type):
        try:
            resource.validate_return_type(return_type)
        except UnknownReturnTypeError:
            pytest.fail(f'_validate_return_type raised an error with return type {return_type}')


@pytest.mark.parametrize(('given_types', 'expected_types'), [
    (['string', 'bool'], (str, bool)),
    (['int', 'uint', 'timestamp'], (int, int, int)),
    (['foo', 'bar', 'int'], (str, str, int))
])
def test_get_type_mapping_gives_correct_types(resource, given_types, expected_types):
    assert expected_types == resource.get_type_mapping(given_types)


class TestCheckFieldValue:

    @pytest.mark.parametrize(('name', 'value', 'error_message'), [
        ('dhcp_utilization_status', 'foo', 'must have one of the following values'),
        ('authority', 'foo', 'must have one of the following types'),
        ('email_list', 'foo', 'must be a list of values'),
        ('email_list', ['foo', 4], 'each item of email_list must have one of the following'),
        ('options', {'field': 'foo'}, 'must be a list of values'),
        ('options', [{'field': 'foo'}, 4], 'each item of options must be a dict')
    ])
    def test_method_raises_error_when_field_value_is_incorrect(self, resource, name, value, error_message):
        with pytest.raises(FieldError) as exc_info:
            resource.check_field_value(name, value)

        assert error_message in str(exc_info.value)

    @pytest.mark.parametrize(('name', 'value'), [
        ('dhcp_utilization_status', 'FULL'),
        ('authority', False),
        ('email_list', ['foo@bar.com']),
        # for now we don't check properties inside struct values so we can write any dict for test
        ('options', [{'field': 'foo'}]),
        ('subscribe_settings', {'field': 'foo'})
    ])
    def test_method_does_not_raise_error_when_field_value_is_correct(self, resource, name, value):
        try:
            resource.check_field_value(name, value)
        except FieldError:
            pytest.fail(f'_check_field_value raises unexpected error for field {name} with value {value}')


class TestValidateParams:

    @pytest.mark.parametrize(('parameters', 'error_message'), [
        ({'authority': 'foo'}, "must have one of the following types: ['bool']"),
        ({'contains_address!': '10.0.0.4'}, 'is not a valid modifier')
    ])
    def test_method_raises_error_when_parameters_are_incorrect(self, resource, parameters, error_message):
        with pytest.raises(FieldError) as exc_info:
            resource.validate_params(parameters)

        assert error_message in str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'authority': True},
        {'*Name': 'foo'},
        {'contains_address=': '10.0.0.4'}
    ])
    def test_method_does_not_raise_error_when_parameters_are_correct(self, resource, parameters):
        try:
            resource.validate_params(parameters)
        except FieldError:
            pytest.fail(f'_validate_params raise error with parameters: {parameters}')
