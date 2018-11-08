import re
import time
from typing import List, Dict, Any, Union, Iterator

import requests

from .exceptions import FieldNotFoundError, FunctionNotFoundError, BadParameterError, SearchOnlyFieldError, \
    UnknownReturnTypeError, FieldError, IncompatibleOperationError, MandatoryFieldError
from .helpers import url_join, handle_http_error
from .types import Schema


class Resource:

    def __init__(self, session: requests.Session, wapi_url: str, name: str):
        self._url = wapi_url
        self._name = name
        self._session = session
        self._schema: Schema = None
        self._load_schema()
        # fields we get by default when we fetch resource objects without changing
        # returned fields
        self._default_get_fields: List[str] = []
        # fields necessary to create the resource object in infoblox
        self._default_post_fields: List[str] = []
        # list of all fields inside the schema
        self._fields: List[str] = []
        # list of all functions inside the schema
        self._functions: List[str] = []
        self._compute_fields_and_functions()

    @property
    def documentation(self) -> Schema:
        return self._schema

    @property
    def name(self) -> str:
        return self._name

    @property
    def fields(self) -> List[str]:
        return self._fields

    @property
    def functions(self) -> List[str]:
        return self._functions

    def _load_schema(self) -> None:
        """Loads the model schema."""
        params = {'_schema': '1', '_schema_version': '2', '_get_doc': '1'}
        response = self._session.get(url_join(self._url, self._name), params=params)
        handle_http_error(response)
        self._schema = response.json()

    def _compute_fields_and_functions(self) -> None:
        """Computes the lists of available fields and functions."""
        for field in self._schema['fields']:
            if field.get('wapi_primitive', '') == 'funccall':
                self._functions.append(field['name'])
            else:
                if field['standard_field']:
                    self._default_get_fields.append(field['name'])
                if field.get('supports_inline_funccall', False):
                    self._default_post_fields.append(field['name'])
                self._fields.append(field['name'])

    @staticmethod
    def _get_field_support_information(support_string: str) -> List[str]:
        if not support_string:
            return []
        supports = [char for char in support_string]
        support_information = {'r': 'read', 's': 'search', 'u': 'update', 'w': 'write'}
        return [support_information[support] for support in supports
                if support in support_information]

    @staticmethod
    def _get_field_searchable_information(searchable_string: str) -> List[str]:
        return [search_char for search_char in searchable_string]

    def _get_struct_field_information(self, field: dict) -> dict:
        """
        Get struct field information
        :param field: dict representing field information
        """
        for struct_info in field['schema']['fields']:
            if struct_info.get('wapi_primitive', '') == 'struct':
                self._get_struct_field_information(struct_info)
            else:
                struct_info['supports'] = self._get_field_support_information(struct_info.get('supports', ''))
                struct_info['searchable_by'] = self._get_field_searchable_information(
                    struct_info.get('searchable_by', '')
                )
        return field

    def _get_field_information(self, field: dict) -> dict:
        """
        Process, transform and return field information.
        :param field: a dictionary representing non struct field information.
        """
        new_field = dict(field)
        new_field['supports'] = self._get_field_support_information(new_field.get('supports', ''))

        if new_field.get('wapi_primitive', '') == 'struct':
            return self._get_struct_field_information(new_field)

        new_field['searchable_by'] = self._get_field_searchable_information(
            new_field.get('searchable_by', '')
        )
        return new_field

    def get_field_information(self, name: str) -> dict:
        """
        Returns detailed information about a field.
        :param name: field name.
        """
        if name not in self._fields:
            raise FieldNotFoundError(f'field {name} does not exist for {self._name} object')
        for field in self._schema['fields']:
            if field['name'] == name:
                return self._get_field_information(field)

    def get_function_information(self, name: str) -> dict:
        if name not in self._functions:
            raise FunctionNotFoundError(f'function {name} does not exist for {self._name} object.')
        for field in self._schema['fields']:
            if field['name'] == name:
                new_field: Schema = dict(field)
                new_field['schema']['input_fields'] = [self._get_field_information(field)
                                                       for field in new_field['schema']['input_fields']]
                new_field['schema']['output_fields'] = [self._get_field_information(field)
                                                        for field in new_field['schema']['output_fields']]
                new_field['supports'] = self._get_field_support_information(new_field.get('supports', ''))
                return new_field

    def _validate_return_fields(self, fields: List[str] = None) -> None:
        """
        Validates returned fields passed for rest operations.
        :param fields: list of fields to check.
        """
        error_prefix = 'fields must be a list of strings'
        if not isinstance(fields, list):
            raise BadParameterError(error_prefix)
        for field in fields:
            if field == 'extattrs':  # extattrs is a special field, we don't check it
                continue
            if not isinstance(field, str):
                raise BadParameterError(f'{error_prefix}, but you provide {field}')
            if '.' in field.strip('.'):  # we don't check sub object field
                continue
            # we need to make sure that the field we want to recover is not read-only
            field_info = self.get_field_information(field)
            if field_info['supports'] == ['search']:
                raise SearchOnlyFieldError(f'{field} is a search only field. It cannot be returned')

    @staticmethod
    def _validate_return_type(return_type: str) -> None:
        """Validates if the return type is correct."""
        return_types = ['json', 'xml', 'xml-pretty', 'json-pretty']
        if return_type not in return_types:
            raise UnknownReturnTypeError(f'{return_type} is not a valid return type. Valid values are {return_types}')

    @staticmethod
    def _get_type_mapping(field_types: List[str]) -> tuple:
        """Translates field types to python types and returns it."""
        returned_types = []
        for _type in field_types:
            if _type in ['int', 'uint', 'timestamp']:
                returned_types.append(int)
            elif _type == 'bool':
                returned_types.append(bool)
            else:
                returned_types.append(str)
        return tuple(returned_types)

    @staticmethod
    def _check_single_field_value(name: str = None, value: Any = None, valid_types: tuple = None,
                                  field_types: List[str] = None, is_struct: bool = False,
                                  is_list: bool = False) -> None:
        """
        Helper method fof method _check_field_value which check field value and raises error if needed with
        with appropriate message.
        :param name: field name.
        :param value: field value.
        :param valid_types: list of valid python types for field value.
        :param field_types: list of valid value types defined in wapi documentation.
        :param is_struct: boolean to know if wapi_primitive is struct.
        :param is_list: boolean to know if the value is part of a list.
        """
        if is_struct:
            error_message = f'{name} must be a dict but you provide {value}'
        else:
            error_message = f'{name} must have one of the following types: {field_types} but you provide {value}'
        # we add a prefix message for list items
        if is_list:
            error_message = f'each item of {error_message}'
        if not isinstance(value, valid_types):
            raise FieldError(error_message)

    def _check_field_value(self, name: str = None, value: Any = None, field_info: Schema = None) -> None:
        """
        Checks that field value corresponds to what is known in the documentation.
        :param name: field name.
        :param value: field value.
        :param field_info: field information. Look at method get_field_information.
        """
        field_information = field_info or self.get_field_information(name)
        is_array: bool = field_information['is_array']
        wapi_primitive: str = field_information.get('wapi_primitive', '')
        enum_values: List[Any] = field_information.get('enum_values', [])
        field_types: list = field_information['type']

        # we check enum values
        if enum_values:
            if value not in enum_values:
                raise FieldError(f'{name} must have one of the following values: {enum_values} but you provide {value}')
            return
        # we check non array values
        if not is_array:
            if wapi_primitive and wapi_primitive == 'struct':
                # todo: recursive control.
                self._check_single_field_value(name, value, (dict,), field_types, is_struct=True)
            else:
                self._check_single_field_value(name, value, self._get_type_mapping(field_types), field_types)
            return
        # whe check array values
        if not isinstance(value, list):
            raise FieldError(f'{name} must be a list of values, but you provide {value}')
        for item in value:
            if wapi_primitive and wapi_primitive == 'struct':
                # todo: recursive control.
                self._check_single_field_value(name, item, (dict,), field_types, is_struct=True, is_list=True)
            else:
                self._check_single_field_value(name, item, self._get_type_mapping(field_types), field_types,
                                               is_list=True)

    def _validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validates query string parameters passed to GET operation to filter results.
        :param params:a dict of parameters to validate.
        """
        for name, value in params.items():
            if name[0] == '*':  # we don't handle extensible attributes
                continue
            parts = re.split(r'([~=<>!])', name)
            search_modifiers = parts[1::2]

            field_name = parts[0]
            field_info: Schema = self.get_field_information(field_name)
            for modifier in search_modifiers:
                if modifier not in field_info['searchable_by']:
                    raise FieldError(f'{modifier} is not a valid modifier for field {field_name}')

            self._check_field_value(field_name, value)

    @staticmethod
    def _check_proxy_search_value(proxy_search: str):
        proxies = ['LOCAL', 'GM']
        if not isinstance(proxy_search, str) or proxy_search.upper() not in ['GM', 'LOCAL']:
            raise BadParameterError(f'proxy_search must be in {proxies} but you provide: {proxy_search}')

    def _process_return_field_parameters(self, return_fields: List[str] = None,
                                         return_fields_plus: List[str] = None) -> dict:
        """
        Process and return a dict representing _return_fields and _return_fields_plus parameters.
        The description of parameters is the same as that of the get method.
        """
        parameters = {}
        if return_fields is not None:
            self._validate_return_fields(return_fields)
            parameters['_return_fields'] = ','.join(return_fields)
        # we use either _return_fields or _return_fields+ but not both
        if return_fields_plus is not None and return_fields is None:
            self._validate_return_fields(return_fields_plus)
            # we don't want add fields which are already part of the default fields returned
            # this is the reason of the list comprehension
            new_return_fields = [field for field in return_fields_plus if field not in self._default_get_fields]
            parameters['_return_fields+'] = ','.join(new_return_fields)
        return parameters

    def _process_get_parameters(self, object_ref: str = None, params: dict = None, return_fields: List[str] = None,
                                return_fields_plus: List[str] = None, proxy_search: str = None,
                                return_type: str = 'json') -> dict:
        """
        Process and returns a dict representing query string to pass for the get operation.
        The description of parameters is the same as that of the get method.
        """
        parameters = {}
        # validate return type
        self._validate_return_type(return_type)
        parameters['_return_type'] = return_type
        # validate params
        # we can't search by field name if we provide an object reference
        if params is not None and object_ref is None:
            self._validate_params(params)
            parameters = {**parameters, **params}

        # get _return_fields and _returns_fields+ parameters
        parameters = {**parameters, **self._process_return_field_parameters(return_fields, return_fields_plus)}
        if proxy_search is not None:
            self._check_proxy_search_value(proxy_search)
            parameters['_proxy_search'] = proxy_search.upper()

        return parameters

    def get(self, object_ref: str = None, params: dict = None, return_fields: List[str] = None,
            return_fields_plus: List[str] = None, proxy_search: str = None,
            return_type: str = 'json') -> Union[dict, List[dict]]:
        """
        Performs get operations. Useful to get a specific object using its reference or just a few objects.
        If you know, you will get many objects, it is better to use the method "get_multiple".
        :param object_ref: reference of the object to fetch.
        :param params: query parameters to filter results. Look wapi documentation, for more information.
        :param return_fields: default object fields to return.
        :param return_fields_plus: additional object fields (extensible attributes included) to return in addition of
        default fields.
        :param proxy_search: 'GM' or 'LOCAL'. See wapi documentation for more information.
        :param return_type: data format for returned values. Possible values are 'json', 'json-pretty', 'xml',
         'xml-pretty'
        """
        parameters = self._process_get_parameters(object_ref, params, return_fields, return_fields_plus, proxy_search,
                                                  return_type)
        url = url_join(self._url, self._name)
        if object_ref is not None:
            if not isinstance(object_ref, str):
                raise BadParameterError(f'object_ref must be a string but you provide {object_ref}')
            url = url_join(self._url, object_ref)
        response = self._session.get(url, params=parameters)
        handle_http_error(response)
        return response.json()

    def get_multiple(self, params: dict = None, return_fields: List[str] = None,
                     return_fields_plus: List[str] = None, proxy_search: str = None,
                     return_type: str = 'json') -> Iterator[dict]:
        """
        Helper function to get multiple objects with memory efficiency.
        The description of parameters is the same as that of the get method.
        """
        parameters = self._process_get_parameters(object_ref=None, params=params, return_fields=return_fields,
                                                  return_fields_plus=return_fields_plus, proxy_search=proxy_search,
                                                  return_type=return_type)
        parameters['_return_as_object'] = 1
        parameters['_paging'] = 1
        parameters['_max_results'] = 1000
        next_page = True

        while next_page:
            response = self._session.get(url_join(self._url, self._name), params=parameters)
            handle_http_error(response)
            json_response = response.json()
            if 'next_page_id' in json_response:
                parameters = {'_page_id': json_response['next_page_id']}
            else:
                next_page = False
            yield from json_response['result']

    @staticmethod
    def _process_schedule_and_approval_info(schedule_time: int = None, schedule_now: bool = False,
                                            schedule_predecessor_task: str = None, schedule_warn_level: str = None,
                                            approval_comment: str = None, approval_query_mode: str = None,
                                            approval_ticket_number: int = None) -> dict:
        """
        Process and returns a dict representing a query dict to pass to create, put or delete operations.
        :param schedule_time: timestamp representing the date to perform the operation.
        :param schedule_now: instructs whether to perform the operation now.
        :param schedule_predecessor_task: reference to a previous task to execute before this one.
        :param schedule_warn_level: warn level. Possible values are "WARN" and "NONE".
        :param approval_comment: comment for the approval operation.
        :param approval_query_mode: query mode for the approval operation. Valid values are "true" or "false".
        :param approval_ticket_number: ticket number for the approval operation.
        For more information on those parameters, refer to wapi documentation.
        """
        parameters = {}
        if schedule_time is not None:
            if not isinstance(schedule_time, int) or schedule_time < int(time.time()):
                raise BadParameterError(f'schedule_time must be a positive integer representing a FUTURE TIME '
                                        f'but you provide {schedule_time}')
            parameters['_schedinfo.scheduled_time'] = schedule_time
        if schedule_now:
            if schedule_time is not None:
                raise IncompatibleOperationError('you cannot use _schedinfo.scheduled_time and _schedinfo.schedule_now'
                                                 ' at the same time')
            if not isinstance(schedule_now, bool):
                raise BadParameterError(f'schedule_now must be a boolean but you provide {schedule_now}')
            parameters['_schedinfo.schedule_now'] = 1 if schedule_now else 0
        if schedule_predecessor_task is not None:
            if not isinstance(schedule_predecessor_task, str):
                raise BadParameterError(f'schedule_predecessor_task must be a string but you provide'
                                        f' {schedule_predecessor_task}')
            parameters['_schedinfo.predecessor_task'] = schedule_predecessor_task
        if schedule_warn_level is not None:
            if not isinstance(schedule_warn_level, str) or schedule_warn_level.upper() not in ['WARN', 'NONE']:
                raise BadParameterError(f'schedule_warn_level must be either WARN or NONE but you provide'
                                        f' {schedule_warn_level}')
            parameters['_schedinfo.warnlevel'] = schedule_warn_level.upper()
        if approval_comment is not None:
            if not isinstance(approval_comment, str):
                raise BadParameterError(f'approval_comment must be a string but you provide {approval_comment}')
            parameters['_approvalinfo.comment'] = approval_comment
        if approval_query_mode is not None:
            if not isinstance(approval_query_mode, str) or approval_query_mode.lower() not in ['true', 'false']:
                raise BadParameterError(f'approval_query_mode must be either true or false but you provide'
                                        f' {approval_query_mode}')
            parameters['_approvalinfo.query_mode'] = approval_query_mode.lower()
        if approval_ticket_number is not None:
            if not isinstance(approval_ticket_number, int):
                raise BadParameterError(f'approval_ticket_number must be an integer but you provide'
                                        f' {approval_ticket_number}')
            parameters['_approvalinfo.ticket_number'] = approval_ticket_number
        return parameters

    def create(self, schedule_time: int = None, schedule_now: bool = False, schedule_predecessor_task: str = None,
               schedule_warn_level: str = None, approval_comment: str = None, approval_query_mode: str = None,
               approval_ticket_number: int = None, return_fields: List[str] = None,
               return_fields_plus: List[str] = None, **kwargs) -> Union[str, dict]:
        """
        Create an infoblox object. Returns the reference of the created object or an object with fields specified
        via return_fields or return_fields_plus parameters.
        kwargs representing fields used to create object with their value.
        To know the description of other parameters, refer to the methods _process_schedule_and_approval_info and get.
        """
        payload = {}
        # we check if all mandatory fields are present
        for field in self._default_post_fields:
            if field not in kwargs:
                raise MandatoryFieldError(
                    f'{field} field is mandatory for {self._name} creation but is missing')
        # we check if field is known and supports write operation
        for field, value in kwargs.items():
            if field not in self._fields:
                raise FieldNotFoundError(f'{field} is not a {self._name} field')
            field_info = self.get_field_information(field)
            if 'write' not in field_info['supports']:
                raise FieldError(f'{field} cannot be written, operations supported by this '
                                 f'field are: {field_info["supports"]}')
            self._check_field_value(field, value, field_info)
            payload[field] = value
        # we process schedule and approval information
        parameters = self._process_schedule_and_approval_info(schedule_time=schedule_time, schedule_now=schedule_now,
                                                              schedule_predecessor_task=schedule_predecessor_task,
                                                              schedule_warn_level=schedule_warn_level,
                                                              approval_comment=approval_comment,
                                                              approval_query_mode=approval_query_mode,
                                                              approval_ticket_number=approval_ticket_number)
        # we process return fields information
        parameters = {**parameters, **self._process_return_field_parameters(return_fields, return_fields_plus)}

        response = self._session.post(url_join(self._url, self._name), params=parameters, json=payload)
        handle_http_error(response)
        return response.json()

    @staticmethod
    def _check_object_reference(object_ref=None) -> None:
        """Checks that object_ref parameter is present and represents a string."""
        if object_ref is None:
            raise MandatoryFieldError('object_ref is missing')
        if not isinstance(object_ref, str):
            raise BadParameterError(f'object_ref must be a string but you provide {object_ref}')

    def modify(self, object_ref: str = None, schedule_time: int = None, schedule_now: bool = False,
               schedule_predecessor_task: str = None, schedule_warn_level: str = None, approval_comment: str = None,
               approval_query_mode: str = None, approval_ticket_number: int = None, return_fields: List[str] = None,
               return_fields_plus: List[str] = None, **kwargs) -> Union[str, dict]:
        """
        Modify a specific object giving its reference. Returns the reference of the modified object or object
        with fields specified via parameters return_fields or return_fields_plus.
        object_ref: reference of the object to modify.
        kwargs: keyword arguments representing fields object to modify.
        To know the meaning of other parameters, refer to the methods _process_schedule_and_approval_info and get.
        """
        self._check_object_reference(object_ref)
        payload = {}
        for key, value in kwargs.items():
            if key not in self._fields:
                raise FieldNotFoundError(f'{key} is not a {self._name} field')
            field_info = self.get_field_information(key)
            if 'update' not in field_info['supports']:
                raise FieldError(f'{key} cannot be updated, operations supported by this'
                                 f' field are: {field_info["supports"]}')
            self._check_field_value(key, value, field_info)
            payload[key] = value
        # we process schedule and approval information
        parameters = self._process_schedule_and_approval_info(schedule_time=schedule_time, schedule_now=schedule_now,
                                                              schedule_predecessor_task=schedule_predecessor_task,
                                                              schedule_warn_level=schedule_warn_level,
                                                              approval_comment=approval_comment,
                                                              approval_query_mode=approval_query_mode,
                                                              approval_ticket_number=approval_ticket_number)
        # we process return fields information
        parameters = {**parameters, **self._process_return_field_parameters(return_fields, return_fields_plus)}

        response = self._session.put(url_join(self._url, object_ref), params=parameters, json=payload)
        handle_http_error(response)
        return response.json()

    def delete(self, object_ref: str = None, schedule_time: int = None, schedule_now: bool = False,
               schedule_predecessor_task: str = None, schedule_warn_level: str = None, approval_comment: str = None,
               approval_query_mode: str = None, approval_ticket_number: int = None):
        """
        Deletes a specific object giving its reference.
        object_ref: reference of the object to modify.
        To know the meaning of other parameters, refer to the method _process_schedule_and_approval_info.
        """
        self._check_object_reference(object_ref)
        # we process schedule and approval information
        parameters = self._process_schedule_and_approval_info(schedule_time=schedule_time, schedule_now=schedule_now,
                                                              schedule_predecessor_task=schedule_predecessor_task,
                                                              schedule_warn_level=schedule_warn_level,
                                                              approval_comment=approval_comment,
                                                              approval_query_mode=approval_query_mode,
                                                              approval_ticket_number=approval_ticket_number)
        response = self._session.delete(url_join(self._url, object_ref), params=parameters)
        handle_http_error(response)
        return response.json()

    @staticmethod
    def _get_field_info_from_function_info(function_info: dict = None, field_name: str = None,
                                           field_type: str = 'input') -> dict:
        """
        Helper method to get input or output field information from function information.
        :param function_info: a dict with function information.
        :param field_name: the name of the field which information is requested.
        :param field_type: specify if it an input of output field. The two possible values are "input" and "output".
        By default it is assumed to be "input".
        """
        for field in function_info['schema'][f'{field_type}_fields']:
            if field['name'] == field_name:
                return field

    def func_call(self, object_ref: str = None, function_name: str = None, **kwargs):
        # object_ref validation
        self._check_object_reference(object_ref)
        # function_name validation
        if function_name is None:
            raise MandatoryFieldError('function_name is missing')
        if not isinstance(function_name, str):
            raise BadParameterError(f'function_name must be a string but you provide {function_name}')
        if function_name not in self._functions:
            raise FunctionNotFoundError(f'{function_name} is an unknown function for {self._name} object')

        function_info = self.get_function_information(function_name)
        input_fields: List[str] = [field['name'] for field in function_info['schema']['input_fields']]

        payload = {}
        for key, value in kwargs.items():
            if key not in input_fields:
                raise BadParameterError(f'{key} is not a valid input field for {function_name} function')
            self._check_field_value(key, value, self._get_field_info_from_function_info(function_info, key))
            payload[key] = value

        parameters = {'_function': function_name}
        response = self._session.post(url_join(self._url, object_ref), params=parameters, json=payload)
        handle_http_error(response)
        return response.json()

    def has_at_least_x_objects(self, number: int) -> bool:
        # don't forget negative max results :)
        pass
