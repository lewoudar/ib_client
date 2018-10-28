from typing import Tuple, List, Dict, Any, Union

import requests

from .exceptions import FieldNotFoundError, FunctionNotFoundError, BadParameterError, SearchOnlyFieldError
from .helpers import url_join, handle_http_error
from .types import Schema


class Resource:

    def __init__(self, session: requests.Session, wapi_url: str, name: str):
        self._url = wapi_url
        self._session = session
        self._name = name
        self._schema: Schema = None
        self._load_schema()
        self._fields, self._functions = self._get_fields_and_functions()

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

    def _get_fields_and_functions(self) -> Tuple[List[str], List[str]]:
        """Returns the lists of available fields and functions."""
        fields = []
        functions = []

        for field in self._schema['fields']:
            if field.get('wapi_primitive', '') == 'funccall':
                functions.append(field['name'])
            else:
                fields.append(field['name'])
        return fields, functions

    @staticmethod
    def _get_field_support_information(support_string: str) -> List[str]:
        if not support_string:
            return []
        supports = [char for char in support_string]
        support_information = {'r': 'read', 's': 'search', 'u': 'update', 'w': 'create'}
        return [support_information[support] for support in supports
                if support in support_information]

    @staticmethod
    def _get_field_searchable_information(searchable_string: str) -> List[str]:
        return [search_char for search_char in searchable_string]

    def _get_field_information(self, field: dict) -> dict:
        """
        Process, transform and return field information.
        :param field: a dictionary representing field information.
        """
        new_field = dict(field)
        new_field['supports'] = self._get_field_support_information(new_field.get('supports', ''))
        new_field['searchable_by'] = self._get_field_searchable_information(
            new_field.get('searchable_by', '')
        )
        return new_field

    def get_field_information(self, name: str) -> Dict[str, Any]:
        """
        Returns detailed information about a field.
        :param name: field name.
        """
        if name not in self._fields:
            raise FieldNotFoundError(f'field {name} does not exist for {self._name} object')
        for field in self._schema['fields']:
            if field['name'] == name:
                return self._get_field_information(field)

    def get_function_information(self, name: str) -> Dict[str, Any]:
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
            # we need to make sure that the field we want to recover is not read-only
            field_info = self.get_field_information(field)
            if field_info['supports'] == ['search']:
                raise SearchOnlyFieldError(f'{field} is a search only field. It cannot be returned')

    def get(self, max_results: int = 1000, params: dict = None, return_fields: List[str] = None,
            return_fields_plus: List[str] = None, return_as_object: bool = False, paging: bool = False,
            proxy_search: str = None, return_type: str = None) -> Union[dict, list]:
        """
        Performs infoblox get operations.
        :param max_results: number of objects to return.
        :param params: query parameters to filter results. Look wapi documentation, for more information.
        :param return_fields: default object fields to return.
        :param return_fields_plus: additional object fields, extensible attributes to return in addition of
        :param return_as_object: boolean which must be true to perform paging requests.
        :param paging: boolean to perform paging requests.
        :param proxy_search: 'GM' or 'local'. See wapi documentation for more information.
        :param return_type: data format for returned values. Possible values are 'json', 'json-pretty', 'xml',
         'xml-pretty'
        :return: a dict or list of dicts.
        """

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
