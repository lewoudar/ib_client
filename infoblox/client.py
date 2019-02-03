import os
import re
import warnings
from typing import List
from typing import Union, Tuple
from urllib.parse import urlparse

import requests
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from ._helpers import handle_http_error, url_join
from ._settings import DEFAULT_CONNECT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_READ_TIMEOUT, DEFAULT_BACKOFF_FACTOR
from .exceptions import IncompatibleApiError, BadParameterError, ObjectNotFoundError, FileError
from .resource import Resource
from .types import Schema, Json

URL_PATH_REGEX = re.compile(r'/wapi/v\d\.\d+')


class Client:

    def __init__(self, wapi_url: str = None, cert: Union[str, Tuple[str, str]] = None, dot_env_path: str = None,
                 user: str = None, password: str = None):
        self._handle_dot_env_file(dot_env_path)
        self._user = user if user is not None else os.getenv('IB_USER')
        self._password = password if password is not None else os.getenv('IB_PASSWORD')
        self._timeout = (float(os.getenv('IB_REQUEST_CONNECT_TIMEOUT', DEFAULT_CONNECT_TIMEOUT)),
                         float(os.getenv('IB_REQUEST_READ_TIMOUT', DEFAULT_READ_TIMEOUT)))
        self._session = requests.Session()
        self._configure_request_retries()
        self._set_session_credentials_and_certificate(cert)
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
    def _handle_dot_env_file(dot_env_path: str = None) -> None:
        """Checks .env file presence and loads it."""
        if dot_env_path is None:
            return
        if not isinstance(dot_env_path, str):
            raise BadParameterError('dot_env_path must be a string')
        if not os.path.isfile(dot_env_path):
            raise FileError(f'{dot_env_path} is not a valid path')
        load_dotenv(dotenv_path=dot_env_path)

    def _configure_request_retries(self) -> None:
        """Configure requests retries mechanism."""
        max_retries = int(os.getenv('IB_MAX_RETRIES', DEFAULT_MAX_RETRIES))
        backoff_factor = float(os.getenv('IB_REQUEST_BACKOFF_FACTOR', DEFAULT_BACKOFF_FACTOR))
        retries = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504])
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)

    def _set_session_credentials_and_certificate(self, cert: Union[str, Tuple[str, str]] = None) -> None:
        """
        Set user credentials and the client certificate if specified.
        :param cert: It may be a single path to the client certificate or a a tuple (certificate, private key).
        For more information, see requests documentation
        http://docs.python-requests.org/en/master/user/advanced/#client-side-certificates
        """
        if cert is None:
            self._session.verify = False
        else:
            self._session.cert = cert
        self._session.auth = (self._user, self._password)

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
        params = {'_schema': 1, '_schema_version': 2}
        # if we don't add a "/" at the end of the url, we will get a 400 status error
        url = self._url if self._url.endswith('/') else f'{self._url}/'
        response = self._session.get(url, params=params, timeout=self._timeout)
        handle_http_error(response)
        self._schema = response.json()

    def get_object(self, name: str) -> Resource:
        """Gets a resource object given an object name supported by wapi."""
        if name not in self.available_objects:
            raise ObjectNotFoundError(f'{name} is not a valid infoblox object')
        return Resource(self._session, self._url, name)

    def custom_request(self, data: Json = None):
        """
        Makes a custom request using the wapi request object.
        :param data: request payload.
        """
        if data is None:
            raise BadParameterError('data must not be empty')
        response = self._session.post(url_join(self._url, 'request'), json=data, timeout=self._timeout)
        handle_http_error(response)
        return response.json()
