import os
import re
import warnings
from typing import List
from typing import Union, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from ._helpers import handle_http_error, url_join
from .exceptions import IncompatibleApiError, BadParameterError, ObjectNotFoundError, FileError
from .resource import Resource
from .types import Schema, Json

URL_PATH_REGEX = re.compile(r'/wapi/v\d\.\d+')


class IBClient:

    def __init__(self, wapi_url: str = None, cert: Union[str, Tuple[str, str]] = None, dot_env_path: str = None):
        self._check_dot_env_file_presence(dot_env_path)
        self._session = requests.Session()
        self._set_session_credentials(cert)
        self._url: str = self._get_start_url(wapi_url)
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
    def _check_dot_env_file_presence(dot_env_path: str = None) -> None:
        """Checks .env file presence and loads it."""
        if dot_env_path is None:
            return
        if not isinstance(dot_env_path, str):
            raise BadParameterError('dot_env_path must be a string')
        if not os.path.isfile(dot_env_path):
            raise FileError(f'{dot_env_path} is not a valid path')
        load_dotenv(dotenv_path=dot_env_path)

    def _set_session_credentials(self, cert: Union[str, Tuple[str, str]] = None) -> None:
        """
        Set the client certificate or ignore verifying the client certificate
        :param cert: It may be a single path to the client certificate or a a tuple (certificate, private key).
        For more information, see requests documentation
        http://docs.python-requests.org/en/master/user/advanced/#client-side-certificates
        """
        if cert is None:
            self._session.verify = False
        else:
            self._session.cert = cert
        self._session.auth = (os.getenv('IB_USER'), os.getenv('IB_PASSWORD'))

    @staticmethod
    def _get_start_url(url: str = None) -> str:
        """Returns the base url to perform further wapi requests."""
        url = url or os.getenv('IB_URL')
        if url is None:
            raise BadParameterError('you must provide url either by passing wapi_url in the __init__ method '
                                    'or by setting environment variable IB_URL')
        error_message = f'{url} is not a valid http url'
        if not isinstance(url, str):
            raise BadParameterError(error_message)
        result = urlparse(url)
        if result.scheme not in ['http', 'https']:
            raise BadParameterError(error_message)
        if not URL_PATH_REGEX.match(result.path):
            raise BadParameterError(f'the url must be in the form http://host/wapi/vX.X, but you supplied: {url}')
        return f'{result.scheme}://{result.netloc}{result.path}'

    @staticmethod
    def _check_api_version(url: str) -> None:
        """Checks if the api version is compatible with the project."""
        url_parts = url.split('/')
        version = url_parts[-1] if url_parts[-1].startswith('v') else url_parts[-2]
        if int(version[1]) <= 1:
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
        """Gets a resource object given an object name supported by wapi."""
        if name not in self.available_objects:
            raise ObjectNotFoundError(f'there is no object {name} in current wapi api')
        return Resource(self._session, self._url, name)

    def custom_request(self, data: Json = None):
        """
        Makes a custom request using the wapi request object.
        :param data: request payload.
        """
        if data is None:
            raise BadParameterError('data must not be empty')
        response = self._session.post(url_join(self._url, 'request'), json=data)
        handle_http_error(response)
        return response.json()
