import re
from typing import List, Dict, Any, Union, Iterator

import requests

from .exceptions import FieldNotFoundError, FunctionNotFoundError, BadParameterError, SearchOnlyFieldError, \
    UnknownReturnTypeError, FieldError
from .helpers import url_join, handle_http_error
from .types import Schema

Get = Union[dict, List[dict], Iterator[dict]]


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
        self._fields: List[str] = []
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

    def get(self, max_results: int = 1000, params: dict = None, return_fields: List[str] = None,
            return_fields_plus: List[str] = None, paging: bool = False, proxy_search: str = None,
            return_type: str = 'json') -> Get:
        """
        Performs get operations.
        :param max_results: number of objects to return.
        :param params: query parameters to filter results. Look wapi documentation, for more information.
        :param return_fields: default object fields to return.
        :param return_fields_plus: additional object fields, extensible attributes to return in addition of
        :param paging: boolean to perform paging requests.
        :param proxy_search: 'GM' or 'LOCAL'. See wapi documentation for more information.
        :param return_type: data format for returned values. Possible values are 'json', 'json-pretty', 'xml',
         'xml-pretty'
        :return: a dict or list of dicts.
        """
        parameters = {}
        # validate return type
        self._validate_return_type(return_type)
        parameters['_return_type'] = return_type
        # validate params
        if params is not None:
            self._validate_params(params)
            parameters = {**parameters, **params}

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
        if proxy_search is not None:
            proxies = ['GM', 'LOCAL']
            if proxy_search.upper() not in ['GM', 'LOCAL']:
                raise BadParameterError(f'proxy_search must be in {proxies} but you provide: {proxy_search}')
            parameters['_proxy_search'] = proxy_search.upper()

        response = self._session.get(url_join(self._url, self._name), params=parameters)
        handle_http_error(response)
        return response.json()
        # if not paging:
        #     response = self._session.get(url_join(self._url, self._name), params=parameters)
        #     handle_http_error(response)
        #     return response.json()
        # else:
        #     if not isinstance(max_results, int):
        #         raise BadParameterError(f'max_results must be an integer but you provide {max_results}')
        #     next_page = True
        #     new_params = {**parameters, **{'_return_as_object': '1', '_paging': '1', '_max_results': max_results}}
        #     while next_page:
        #         response = self._session.get(url_join(self._url, self._name), params=new_params)
        #         handle_http_error(response)
        #         json_response = response.json()
        #         if 'next_page_id' in json_response:
        #             new_params = {'_page_id': json_response['next_page_id']}
        #             yield from json_response['result']
        #         else:
        #             next_page = False

    def get_all_objects(self):
        pass

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def func_call(self):
        pass

    def has_at_least_x_objects(self, number: int) -> bool:
        # don't forget negative max results :)
        pass
