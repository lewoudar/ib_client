"""Tests some intern methods and properties defined in Resource class"""
import time

import pytest

from infoblox.exceptions import BadParameterError, FieldNotFoundError, SearchOnlyFieldError, \
    FieldError, FunctionNotFoundError, IncompatibleOperationError, NotSearchableFieldError, MandatoryFieldError


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


class TestResourceProperties:
    def test_documentation_property_contains_correct_info(self, resource):
        for item in ['cloud_additional_restrictions', 'fields', 'restrictions', 'schema_version', 'type', 'version',
                     'wapi_primitive']:
            assert item in resource.documentation

    def test_name_property_is_correct(self, resource_name, resource):
        assert resource_name == resource.name

    def test_fields_property_contains_correct_info(self, resource):
        for item in ['comment', 'network', 'contains_address']:
            assert item in resource.fields
        # expand_network is a function, it should be in fields property
        assert 'expand_network' not in resource.fields

    def test_functions_property_contains_correct_info(self, resource):
        assert 'expand_network' in resource.functions
        # authority is a field, not a function so it should not be in functions property
        assert 'authority' not in resource.functions


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
        ({'ipv4addr': True}, "must have one of the following types: ['string']"),
        ({'contains_address!': '10.0.0.4'}, 'is not a valid modifier')
    ])
    def test_method_raises_error_when_parameters_are_incorrect(self, resource, parameters, error_message):
        with pytest.raises(FieldError) as exc_info:
            resource.validate_params(parameters)

        assert error_message in str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'authority': True},
        {'email_list': ['']}
    ])
    def test_method_raises_error_when_parameters_are_not_searchable(self, resource, parameters):
        with pytest.raises(NotSearchableFieldError) as exc_info:
            resource.validate_params(parameters)

        assert 'is not searchable' in str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'*Name': 'foo'},
        {'contains_address': '10.0.0.4'}
    ])
    def test_method_does_not_raise_error_when_parameters_are_correct(self, resource, parameters):
        try:
            resource.validate_params(parameters)
        except FieldError:
            pytest.fail(f'_validate_params raise error with parameters: {parameters}')


class TestCheckProxySearchValue:
    @pytest.mark.parametrize('proxy_search', [4, 'foo'])
    def test_method_raises_error_when_proxy_search_is_incorrect(self, resource, proxy_search):
        with pytest.raises(BadParameterError) as exc_info:
            resource.check_proxy_search_value(proxy_search)

        assert 'proxy_search must be in' in str(exc_info.value)

    @pytest.mark.parametrize('proxy_search', ['GM', 'local', 'Gm', 'locAl'])
    def test_method_does_not_raise_error_when_proxy_search_is_correct(self, resource, proxy_search):
        try:
            resource.check_proxy_search_value(proxy_search)
        except BadParameterError:
            pytest.fail(f'_check_proxy_search raises an error with value {proxy_search}')


class TestCheckObjectReference:

    def test_method_raises_error_when_object_ref_is_missing(self, resource):
        with pytest.raises(MandatoryFieldError) as exc_info:
            resource.check_object_reference()

        assert 'object_ref is missing' == str(exc_info.value)

    @pytest.mark.parametrize('object_ref', [4, {}, []])
    def test_method_raises_error_when_object_ref_is_not_a_string(self, resource, object_ref):
        with pytest.raises(BadParameterError) as exc_info:
            resource.check_object_reference(object_ref)

        assert f'object_ref must be a string but you provide {object_ref}' == str(exc_info.value)


class TestProcessScheduleAndApprovalInfo:

    @pytest.mark.parametrize(('parameters', 'error_message'), [
        ({'schedule_time': 'foo'}, 'schedule_time must be a positive integer representing a FUTURE TIME'),
        ({'schedule_time': 12}, 'schedule_time must be a positive integer representing a FUTURE TIME'),
        ({'schedule_now': 'foo'}, 'schedule_now must be a boolean'),
        ({'schedule_now': 2}, 'schedule_now must be a boolean'),
        ({'schedule_predecessor_task': 2}, 'schedule_predecessor_task must be a string'),
        ({'schedule_predecessor_task': 2.0}, 'schedule_predecessor_task must be a string'),
        ({'schedule_warn_level': 2.0}, 'schedule_warn_level must be either WARN or NONE'),
        ({'schedule_warn_level': 'foo'}, 'schedule_warn_level must be either WARN or NONE'),
        ({'approval_comment': 2}, 'approval_comment must be a string'),
        ({'approval_comment': 2.0}, 'approval_comment must be a string'),
        ({'approval_query_mode': 2}, 'approval_query_mode must be either true or false'),
        ({'approval_query_mode': 'foo'}, 'approval_query_mode must be either true or false'),
        ({'approval_ticket_number': 2.0}, 'approval_ticket_number must be an integer'),
        ({'approval_ticket_number': 'foo'}, 'approval_ticket_number must be an integer')
    ])
    def test_method_raises_error_when_parameters_are_incorrect(self, resource, parameters, error_message):
        with pytest.raises(BadParameterError) as exc_info:
            resource.process_schedule_and_approval_info(**parameters)

        assert error_message in str(exc_info.value)

    def test_method_raises_error_if_schedule_time_and_schedule_now_are_both_set(self, resource):
        with pytest.raises(IncompatibleOperationError) as exc_info:
            resource.process_schedule_and_approval_info(schedule_time=int(time.time()) + 10, schedule_now=True)

        assert 'you cannot use _schedinfo.scheduled_time and _schedinfo.schedule_now' \
               ' at the same time' == str(exc_info.value)

    @pytest.mark.parametrize('parameters', [
        {'schedule_time': int(time.time()) + 10},
        {'schedule_now': True},
        {'schedule_predecessor_task': 'previous-task'},
        {'schedule_warn_level': 'WARN'},
        {'approval_comment': 'comment'},
        {'approval_query_mode': 'true'},
        {'approval_ticket_number': 12}
    ])
    def test_method_does_not_raise_error_when_parameters_are_correct(self, resource, parameters):
        try:
            resource.process_schedule_and_approval_info(**parameters)
        except BadParameterError:
            pytest.fail(f'_process_schedule_and_approval_info raises error with parameters {parameters}')

    @pytest.mark.parametrize(('parameters', 'expected_query_dict'), [
        (
                {'schedule_now': True, 'schedule_predecessor_task': 'previous-task'},
                {'_schedinfo.schedule_now': 1, '_schedinfo.predecessor_task': 'previous-task'}
        ),
        (
                {'schedule_warn_level': 'NONE', 'approval_comment': 'comment'},
                {'_schedinfo.warnlevel': 'NONE', '_approvalinfo.comment': 'comment'}
        ),
        (
                {'approval_query_mode': 'false', 'approval_ticket_number': 1452},
                {'_approvalinfo.query_mode': 'false', '_approvalinfo.ticket_number': 1452}
        )
    ])
    def test_method_returns_correct_query_dict(self, resource, parameters, expected_query_dict):
        assert expected_query_dict == resource.process_schedule_and_approval_info(**parameters)

    # we write a specific test case for schedule_time because it is not simple to handle common time
    # between fixture parameters (parameters and expected_query_dict)
    @pytest.mark.parametrize(('parameters', 'expected_query_dict'), [
        (
                {'schedule_warn_level': 'NONE', 'approval_comment': 'comment'},
                {'_schedinfo.warnlevel': 'NONE', '_approvalinfo.comment': 'comment'}
        ),
        (
                {'approval_query_mode': 'false', 'approval_ticket_number': 1452},
                {'_approvalinfo.query_mode': 'false', '_approvalinfo.ticket_number': 1452}
        )
    ])
    def test_method_returns_correct_query_dict_when_giving_correct_schedule_time(self, resource, parameters,
                                                                                 expected_query_dict):
        schedule_time = int(time.time()) + 10
        parameters['schedule_time'] = schedule_time
        expected_query_dict['_schedinfo.scheduled_time'] = schedule_time
        assert expected_query_dict == resource.process_schedule_and_approval_info(**parameters)
