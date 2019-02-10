from collections import namedtuple

import pytest
from requests import ConnectionError

from infoblox.scripts import cli
from tests.helpers import assert_in_output


def test_cli_raises_error_if_env_variable_is_not_set(runner):
    result = runner.invoke(cli, ['objects'])

    assert_in_output(2, 'environment variable must be set before using ib', result)


@pytest.mark.usefixtures('env_settings')
def test_cli_raises_error_when_requests_raises_connection_error(runner, mocker):
    class CustomContainer:
        def __init__(self):
            raise ConnectionError

    mocker.patch('infoblox.scripts.Container', new=CustomContainer)
    result = runner.invoke(cli, ['objects'])

    assert_in_output(1, 'The remote server is unreachable', result)


@pytest.mark.usefixtures('env_settings')
@pytest.mark.parametrize('env_variable', ['IB_REQUEST_MAX_RETRIES', 'IB_REQUEST_CONNECT_TIMEOUT'])
def test_cli_raises_error_when_env_variable_is_incorrect(runner, mocker, env_variable):
    mocker.patch.dict('os.environ', {env_variable: 'foo'})
    result = runner.invoke(cli, ['objects'])

    assert_in_output(1, 'You have probably mistaken value for an environment variable', result)


def test_cli_calls_function_handle_dot_env_file(mocker, runner):
    # we simulate a container with a client to prevent errors when the underlying call is performed:
    # context.obj.client.available_objects
    Container = namedtuple('Container', ['client'])
    Client = namedtuple('Client', ['available_objects'])
    container_mock = mocker.patch('infoblox.scripts.Container')
    container_mock.return_value = Container(client=Client(available_objects={'foo': 'bar'}))

    with runner.isolated_filesystem():
        with open('.env', 'w') as stream:
            url = 'https://foo/wapi/v2.9'
            user = password = 'foo'
            stream.writelines([f'IB_URL={url}\n', f'IB_USER={user}\n', f'IB_PASSWORD={password}'])

        result = runner.invoke(cli, ['objects'])
        assert 0 == result.exit_code
