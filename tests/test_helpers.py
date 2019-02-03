import json

import pytest
from requests import Response

# noinspection PyProtectedMember
from infoblox._helpers import url_join, handle_http_error
from infoblox.exceptions import BadParameterError, HttpError


@pytest.fixture
def response():
    return Response()


class TestUrlJoin:
    @pytest.mark.parametrize(('base_url', 'path'), [
        (4, 'foo'),
        ('foo', 4),
        (4, 4)
    ])
    def test_function_raises_error_when_an_argument_is_not_a_string(self, base_url, path):
        with pytest.raises(BadParameterError) as exc_info:
            url_join(base_url, path)

        assert 'is not a string' in str(exc_info.value)

    @pytest.mark.parametrize(('base_url', 'path', 'expected_result'), [
        ('http://localhost', 'foo', 'http://localhost/foo'),
        ('http://localhost/', 'foo/', 'http://localhost/foo/'),
        ('http://localhost', '/foo', 'http://localhost/foo'),
        ('http://localhost/', '/foo', 'http://localhost/foo')
    ])
    def test_function_returns_correct_url(self, base_url, path, expected_result):
        assert expected_result == url_join(base_url, path)


class TestHandleHttpError:

    @pytest.mark.parametrize('status_code', [400, 500])
    def test_function_raises_error_when_status_code_greater_or_equal_than_400(self, response, status_code):
        response.status_code = status_code
        response._content = ''

        with pytest.raises(HttpError):
            handle_http_error(response)

    @pytest.mark.parametrize('status_code', [200, 300])
    def test_function_does_not_raises_error_when_status_code_is_less_than_400(self, response, status_code):
        response.status_code = status_code
        response._content = ''
        try:
            handle_http_error(response)
        except HttpError:
            pytest.fail(f'handle_http_error raises an HttpError with status_code = {status_code}')

    def test_function_returns_correct_status_code_and_error_message_with_json_message(self, response):
        status_code = 400
        error_message = {'error': 'oops'}
        response.status_code = status_code
        response.encoding = 'utf-8'
        response._content = json.dumps(error_message).encode('utf-8')
        try:
            handle_http_error(response)
        except HttpError as e:
            assert status_code == e.status_code
            assert error_message == e.error_message

    def test_function_returns_correct_status_code_and_error_message_with_text_message(self, response):
        status_code = 400
        error_message = 'error'
        response.status_code = status_code
        response.encoding = 'utf-8'
        response._content = error_message.encode('utf-8')

        try:
            handle_http_error(response)
        except HttpError as e:
            assert status_code == e.status_code
            assert error_message == e.error_message
