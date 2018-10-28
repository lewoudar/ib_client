import os
import warnings
from typing import List
from urllib.parse import urlparse

import requests

from .resource import Resource
from .exceptions import IncompatibleApiError, BadParameterError, ObjectNotFoundError
from .helpers import handle_http_error
from .types import Schema


class IBClient:

    def __init__(self, wapi_url: str = None):
        self._session = requests.Session()
        self._session.auth = (os.environ.get('IB_USER'), os.environ.get('IB_PASSWORD'))
        self._url: str = self._get_start_url(wapi_url) if wapi_url is not None else\
            self._get_start_url(os.environ.get('IB_URL'))
        self._schema: Schema = None
        # we load the api schema
        self._load_schema()

    @property
    def api_schema(self) -> Schema:
        return self._schema

    @property
    def available_objects(self) -> List[str]:
        return self._schema['supported_objects']

    @staticmethod
    def _get_start_url(url: str) -> str:
        """Returns the base url to perform further wapi requests."""
        error_message = f'{url} is not a valid http url'
        if not isinstance(url, str):
            raise BadParameterError(error_message)
        result = urlparse(url)
        if result.scheme not in ['http', 'https']:
            raise BadParameterError(error_message)
        if not result.path.startswith('/wapi/v'):
            raise BadParameterError(f'the url must be in the form http://host/wapi/vX.X, but you supplied: {url}')
        return f'{result.scheme}://{result.netloc}{result.path}'

    @staticmethod
    def _check_api_version(url: str) -> None:
        url_parts = url.split('/')
        version = url_parts[-1] if url_parts[-1].startswith('v') else url_parts[-2]
        if version[1] == '1':
            raise IncompatibleApiError('the client supports in priority major version 2 of the api')
        if int(version[1]) >= 3:
            warnings.warn(f'The client is in priority for major version 2,'
                          f' not sure it works correctly for {version[1]}')

    def _load_schema(self) -> None:
        """Returns the api schema."""
        # we check if the api version is supported
        self._check_api_version(self._url)
        params = {'_schema': 1, '_schema_version': 2, '_schema_searchable': 1}
        response = self._session.get(self._url, params=params)
        handle_http_error(response)
        self._schema = response.json()

    def get_object(self, name: str) -> Resource:
        if name not in self.available_objects:
            raise ObjectNotFoundError(f'there is no object {name} in current wapi api.')
        return Resource(self._session, self._url, name)

    def custom_request(self):
        # request api
        pass

    def upload_file(self, filename: str) -> None:
        # todo: don't forget to do this
        pass

    def download_file(self, filename: str):
        pass
