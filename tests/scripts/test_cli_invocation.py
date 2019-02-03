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
