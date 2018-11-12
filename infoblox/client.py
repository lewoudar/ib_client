import os
import warnings
from typing import List
from urllib.parse import urlparse
from typing import Union, Tuple

import requests
from dotenv import load_dotenv

from .resource import Resource
from .exceptions import IncompatibleApiError, BadParameterError, ObjectNotFoundError, FileError
from ._helpers import handle_http_error
from .types import Schema


class IBClient:

    def __init__(self, wapi_url: str = None, cert: Union[str, Tuple[str, str]] = None, dot_env_path: str = None):
        self._check_if_dot_env_file(dot_env_path)
        self._session = requests.Session()
        if cert is None:
            self._session.verify = False
        else:
            self._session.cert = cert
        self._session.auth = (os.getenv('IB_USER'), os.getenv('IB_PASSWORD'))
        self._url: str = self._get_start_url(wapi_url) if wapi_url is not None else \
            self._get_start_url(os.getenv('IB_URL'))
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
    def _check_if_dot_env_file(dot_env_path: str = None) -> None:
        """Checks .env file presence and loads it."""
        if dot_env_path is None:
            return
        if not isinstance(dot_env_path, str):
            raise BadParameterError('dot_env_path must be a string')
        if not os.path.isfile(dot_env_path):
            raise FileError(f'{dot_env_path} is not a valid path')
        load_dotenv(dotenv_path=dot_env_path)

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
