from infoblox.scripts import cli


def test_cli_raises_error_if_env_variable_is_not_set(runner):
    result = runner.invoke(cli, ['objects'])

    assert 2 == result.exit_code
    assert 'environment variable must be set before using ib' in result.output
