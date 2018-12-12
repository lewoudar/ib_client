import json
import os
import tempfile

import pytest

from infoblox.client import IBClient
from infoblox.exceptions import BadParameterError, FileError, IncompatibleApiError, HttpError, ObjectNotFoundError
from infoblox.resource import Resource


class TestDotEnvFile:
    # test method _check_dot_env_file_presence
    class Client(IBClient):
        @staticmethod
        def check_dot_env_file_presence(env_path=None):
            return IBClient._check_dot_env_file_presence(env_path)

    def test_method_returns_none_when_parameter_is_none(self):
        assert self.Client.check_dot_env_file_presence() is None

    @pytest.mark.parametrize('env_path', [4, 4.0])
    def test_method_raises_error_when_parameter_is_not_a_string(self, env_path):
        with pytest.raises(BadParameterError) as exc_info:
            self.Client.check_dot_env_file_presence(env_path)

        assert 'dot_env_path must be a string' == str(exc_info.value)

    @pytest.mark.parametrize('env_path', ['foo', 'bar'])
    def test_method_raises_error_when_parameter_is_not_a_valid_path(self, env_path):
        with pytest.raises(FileError) as exc_info:
            self.Client.check_dot_env_file_presence(env_path)

        assert f'{env_path} is not a valid path' == str(exc_info.value)

    def test_method_sets_correctly_environment_variables_from_env_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            env_path = os.path.join(tempdir, '.env')
            with open(env_path, 'w') as stream:
                stream.writelines(['FOO=dad\n', 'BAR=mom'])

            self.Client.check_dot_env_file_presence(env_path)

            assert 'dad' == os.getenv('FOO')
            assert 'mom' == os.getenv('BAR')


class TestSetSessionCredentials:
    # test method _set_session_credentials
    class Client(IBClient):
        def set_session_credentials(self, cert=None):
            self._set_session_credentials(cert)

        @property
        def session(self):
            return self._session

    def test_method_sets_verify_session_attribute_to_false_when_parameter_is_none(self, mocker):
        mocker.patch('infoblox.client.IBClient._load_schema')
        client = self.Client('http://foo/wapi/v2.9')
        client.set_session_credentials()

        assert client.session.verify is False

    @pytest.mark.parametrize('certificate', ['foo', ('foo', 'foo')])
    def test_method_raises_error_when_parameter_is_an_invalid_path(self, mocker, certificate):
        mocker.patch('infoblox.client.IBClient._load_schema')
        client = self.Client('http://foo/wapi/v2.9')
        client.set_session_credentials(certificate)

        with pytest.raises(OSError):
            # we need to make a request to trigger the error
            client.session.get('https://foo.com')

    def test_method_raises_error_when_certificate_is_not_correct(self, mocker):
        mocker.patch('infoblox.client.IBClient._load_schema')
        client = self.Client('http://foo/wapi/v2.9')
        with tempfile.TemporaryDirectory() as tempdir:
            certificate_path = os.path.join(tempdir, 'cert.pem')
            with open(certificate_path, 'w') as stream:
                stream.write('fake certificate')

            client.set_session_credentials(certificate_path)
            with pytest.raises(OSError):
                client.session.get('https://foo.com')

    def test_method_sets_user_and_password_information(self, mocker):
        mocker.patch('infoblox.client.IBClient._load_schema')
        with tempfile.TemporaryDirectory() as tempdir:
            env_file = os.path.join(tempdir, '.env')
            with open(env_file, 'w') as stream:
                stream.writelines(['IB_USER=foo\n', 'IB_PASSWORD=bar'])
            client = self.Client('http://foo/wapi/v2.9', dot_env_path=env_file)
            client.set_session_credentials()

            assert ('foo', 'bar') == client.session.auth


class TestGetStartUrl:
    # test method _get_start_url
    class Client(IBClient):
        @staticmethod
        def get_start_url(url=None):
            return IBClient._get_start_url(url)

    def test_method_raises_error_when_parameter_is_missing(self):
        with pytest.raises(BadParameterError) as exc_info:
            self.Client.get_start_url()

        assert 'you must provide url either by passing wapi_url' in str(exc_info.value)

    @pytest.mark.parametrize('url', [4, 4.0])
    def test_method_raises_error_when_parameter_is_not_a_string(self, url):
        with pytest.raises(BadParameterError) as exc_info:
            self.Client.get_start_url(url)

        assert f'{url} is not a valid http url' == str(exc_info.value)

    @pytest.mark.parametrize('url', ['foo', 'ftp://user:pass@foo.com'])
    def test_method_raises_error_when_url_scheme_is_not_http(self, url):
        with pytest.raises(BadParameterError) as exc_info:
            self.Client.get_start_url(url)

        assert f'{url} is not a valid http url' == str(exc_info.value)

    @pytest.mark.parametrize('url', [
        'http://foo',
        'https://host/wapi/',
        'http://foo/wapi/v2',
        'https://foo/wapi/v2.ef'
    ])
    def test_method_raises_error_when_url_does_not_contains_wapi_prefix(self, url):
        with pytest.raises(BadParameterError) as exc_info:
            self.Client.get_start_url(url)

        assert 'the url must be in the form http://host/wapi/vX.X' in str(exc_info.value)

    @pytest.mark.parametrize(('given_url', 'expected_url'), [
        ('http://localhost/wapi/v2.9', 'http://localhost/wapi/v2.9'),
        ('https://localhost/wapi/v5.4/', 'https://localhost/wapi/v5.4/')
    ])
    def test_method_returns_start_url_when_parameter_is_correct(self, given_url, expected_url):
        assert expected_url == self.Client.get_start_url(given_url)


class TestCheckApiVersion:
    # tests method _check_api_version
    class Client(IBClient):
        @staticmethod
        def check_api_version(url):
            IBClient._check_api_version(url)

    @pytest.mark.parametrize('url', ['http://foo/wapi/v1.0', 'https://foo/wapi/v0.3/'])
    def test_method_raises_error_if_wapi_version_is_incompatible(self, url):
        with pytest.raises(IncompatibleApiError):
            self.Client.check_api_version(url)

    @pytest.mark.parametrize('url', ['http://foo/wapi/v3.2', 'https://foo/wapi/v4.0/'])
    def test_method_raises_warning_if_wapi_version_is_greater_than_2(self, mocker, url):
        warn_mock = mocker.patch('warnings.warn')
        self.Client.check_api_version(url)

        warn_mock.assert_called_once()

    @pytest.mark.parametrize('url', ['http://foo/wapi/v2.0', 'https://foo/wapi/v2.6/'])
    def test_method_does_not_raises_error_or_warning_if_wapi_version_equals_to_2(self, mocker, url):
        warn_mock = mocker.patch('warnings.warn')

        try:
            self.Client.check_api_version(url)
        except IncompatibleApiError:
            pytest.fail(f'method _check_api_version raises an error with url: {url}')

        warn_mock.assert_not_called()


class TestLoadSchema:
    # test method _load_schema

    def test_method_called_check_api_version_with_correct_argument(self, mocker, responses, api_schema):
        url = 'http://foo/wapi/v2.9/'
        responses.add(responses.GET, url, json=api_schema, status=200)
        check_api_mock = mocker.patch('infoblox.client.IBClient._check_api_version')
        IBClient(url)

        check_api_mock.assert_called_once_with(url)

    @pytest.mark.parametrize('status_code', [400, 500])
    def test_method_raises_error_when_response_status_code_greater_or_equal_than_400(self, responses, status_code):
        url = 'http://foo/wapi/v2.9/'
        responses.add(responses.GET, url, json={'error': 'oops'}, status=status_code)

        with pytest.raises(HttpError):
            IBClient(url)

    def test_method_loads_schema_when_called_correctly(self, responses, api_schema):
        url = 'http://foo/wapi/v2.9/'
        responses.add(responses.GET, url, json=api_schema, status=200)
        client = IBClient(url)

        assert api_schema == client.api_schema


class TestInit:
    # test __init__ method

    def test_method_calls_mandatory_intern_methods(self, mocker):
        dot_env_mock = mocker.patch('infoblox.client.IBClient._check_dot_env_file_presence')
        set_session_mock = mocker.patch('infoblox.client.IBClient._set_session_credentials')
        start_url_mock = mocker.patch('infoblox.client.IBClient._get_start_url')
        load_schema_mock = mocker.patch('infoblox.client.IBClient._load_schema')

        IBClient('http://foo/wapi/v2.9', 'cert.pem', '.env')

        dot_env_mock.assert_called_once_with('.env')
        set_session_mock.assert_called_once_with('cert.pem')
        start_url_mock.assert_called_once_with('http://foo/wapi/v2.9')
        load_schema_mock.assert_called_once()

    def test_available_objects_property_is_initialized(self, api_schema, client):
        assert api_schema['supported_objects'] == client.available_objects


class TestGetObject:
    # test method get_object
    @pytest.mark.parametrize('object_name', ['foo', 'bar'])
    def test_method_raises_error_if_object_is_not_found(self, client, object_name):
        with pytest.raises(ObjectNotFoundError) as exc_info:
            client.get_object(object_name)

        assert f'there is no object {object_name} in current wapi api' == str(exc_info.value)

    def test_method_returns_a_resource_instance(self, responses, url, network_schema, client):
        object_name = 'network'
        responses.add(responses.GET, f'{url}/{object_name}', json=network_schema, status=200)

        assert isinstance(client.get_object(object_name), Resource)


class TestCustomRequest:
    # test method custom_request
    def test_method_raises_error_when_argument_is_missing(self, client):
        with pytest.raises(BadParameterError) as exc_info:
            client.custom_request()

        assert 'data must not be empty' == str(exc_info.value)

    @pytest.mark.parametrize('status_code', [400, 500])
    def test_method_raises_error_when_response_status_is_greater_or_equal_than_400(self, responses, client, url,
                                                                                   status_code):
        def request_callback(*_):
            return status_code, {}, json.dumps({'error': 'oops'})

        responses.add_callback(responses.POST, f'{url}/request', content_type='application/json',
                               callback=request_callback)
        with pytest.raises(HttpError):
            client.custom_request('foo')

    def test_method_returns_data_when_call_is_correct(self, responses, url, client):
        data = {'hello': 'world'}

        def request_callback(request):
            return 200, {}, request.body

        responses.add_callback(responses.POST, f'{url}/request', content_type='application/json',
                               callback=request_callback)

        assert data == client.custom_request(data)
