import os
import tempfile

import pytest
import requests
from click.testing import CliRunner

from infoblox.client import IBClient
from infoblox.resource import Resource


@pytest.fixture(scope='session')
def api_schema():
    return {
        "requested_version": "2.9",
        "supported_objects": ["ipv4address", "ipv6address", "ipv6network",
                              "ipv6networkcontainer", "ipv6range",
                              "macfilteraddress", "network"],
        "supported_versions": ["1.0", "1.1", "1.2", "1.2.1", '2.0'],
        "schema_version": "2.0",
    }


@pytest.fixture(scope='session')
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
                "doc": "Comment for the network, maximum 256 characters.",
                "is_array": False,
                "name": "comment",
                "searchable_by": ":=~",
                "standard_field": True,
                "supports": "rwus",
                "type": [
                    "string"
                ]
            },
            {
                "doc": "The network address in IPv4 Address/CIDR format. For regular expression searches,"
                       " only the IPv4 Address portion is supported. Searches for the CIDR portion is always"
                       " an exact match. For example, both network containers 10.0.0.0/8 and 20.1.0.0/16 are matched"
                       " by expression '.0' and only 20.1.0.0/16 is matched by '.0/16'.",
                "is_array": False,
                "name": "network",
                "searchable_by": "=~",
                "standard_field": True,
                "supports": "rwus",
                "supports_inline_funccall": True,
                "type": [
                    "string"
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
                                        "doc": "The Cisco ISE attribute name that is enabled for publishsing from"
                                               " a Cisco ISE endpoint.",
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
                "doc": "This function retrieves the next available IP in the network.",
                "is_array": False,
                "name": "next_available_ip",
                "schema": {
                    "input_fields": [
                        {
                            "doc": "The number of IP addresses you are requesting.",
                            "is_array": False,
                            "name": "num",
                            "supports": "w",
                            "type": [
                                "uint"
                            ]
                        },
                        {
                            "doc": "A list of IP addresses to exclude.",
                            "is_array": True,
                            "name": "exclude",
                            "supports": "w",
                            "type": [
                                "string"
                            ]
                        }
                    ],
                    "output_fields": [
                        {
                            "doc": "The requested IP addresses.",
                            "is_array": True,
                            "name": "ips",
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
                    "nextavailableip"
                ],
                "wapi_primitive": "funccall"
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

    def get_type_mapping(self, field_types):
        return self._get_type_mapping(field_types)

    def check_field_value(self, name, value, field_info=None):
        self._check_field_value(name, value, field_info)

    def validate_params(self, params):
        self._validate_params(params)

    def check_proxy_search_value(self, proxy_search: str):
        self._check_proxy_search_value(proxy_search)

    def process_schedule_and_approval_info(self, schedule_time: int = None, schedule_now: bool = False,
                                           schedule_predecessor_task: str = None, schedule_warn_level: str = None,
                                           approval_comment: str = None, approval_query_mode: str = None,
                                           approval_ticket_number: int = None):
        return self._process_schedule_and_approval_info(schedule_time, schedule_now, schedule_predecessor_task,
                                                        schedule_warn_level, approval_comment, approval_query_mode,
                                                        approval_ticket_number)

    def get_field_info_from_function_info(self, function_info, field_name, field_type):
        return self._get_field_info_from_function_info(function_info, field_name, field_type)


@pytest.fixture(scope='session')
def url():
    return 'http://foo/wapi/v2.9'


@pytest.fixture(scope='session')
def resource_name():
    return 'network'


@pytest.fixture
def resource(responses, url, resource_name, network_schema):
    responses.add(responses.GET, f'{url}/{resource_name}', json=network_schema, status=200)
    return MyResource(requests.Session(), url, resource_name)


@pytest.fixture(scope='session')
def runner():
    return CliRunner()


@pytest.fixture
def client(responses, api_schema, url):
    responses.add(responses.GET, f'{url}/', json=api_schema, status=200)
    return IBClient(url)


@pytest.fixture
def env_settings(url):
    """This fixture is useful for scripts testing."""
    os.environ['IB_USER'] = 'foo'
    os.environ['IB_PASSWORD'] = 'foo'
    # the "/" at the end is to avoid an issue with responses fixture when we load the api schema
    os.environ['IB_URL'] = f'{url}/'


@pytest.fixture
def tempdir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
