"""Here we test commands that are not directly related to infoblox."""
import pytest

from infoblox.scripts import cli
from tests.helpers import assert_in_output


@pytest.mark.usefixtures('client', 'env_settings')
class TestShellCompletionCommand:

    @pytest.mark.parametrize('options', [
        [],
        ['--append', '-i', 'bash', '/home/foo/.bash_completion']
    ])
    def test_command_prints_shell_completion_message(self, runner, mocker, options):
        install_path = mocker.patch('click_completion.core.install')
        shell, path = 'bash', '/bin/bash'
        install_path.return_value = (shell, path)

        result = runner.invoke(cli, ['shell-completion', *options])
        assert_in_output(0, f'{shell} completion installed in {path}', result)

    def test_command_prints_error_when_shell_is_not_supported(self, runner):
        shell = 'cmd'
        result = runner.invoke(cli, ['shell-completion', shell, f'{shell}.exe'])
        assert_in_output(2, f'invalid choice: {shell}', result)

    def test_command_prints_error_when_script_path_cannot_be_created(self, runner, mocker):
        def make_dir_fails(*_):
            raise OSError('os error')

        mocker.patch('os.makedirs', new=make_dir_fails)

        result = runner.invoke(cli, ['shell-completion', 'bash', '/fake/path'])
        assert_in_output(1, 'os error', result)
