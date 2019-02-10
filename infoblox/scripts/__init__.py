import click
import click_completion
from click_didyoumean import DYMGroup
from requests import ConnectionError

# noinspection PyProtectedMember
from infoblox import __version__, Client, Resource
from infoblox.scripts.client_commands import api_schema, available_objects, custom_request
from infoblox.scripts.resource_commands import resource
from infoblox.scripts.utils import check_environment, handle_dot_env_file

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
click_completion.init()


class Container:
    def __init__(self):
        self.client = Client()
        self.resource: Resource = None


@click.version_option(__version__)
@click.group(context_settings=CONTEXT_SETTINGS, cls=DYMGroup)
@click.pass_context
def cli(context):
    """
    Infoblox Command Line Interface. It allows you to interact with infoblox in the same way
    you will do with the python api client.
    """
    handle_dot_env_file()
    check_environment()
    try:
        context.obj = Container()
    except ConnectionError:
        raise click.ClickException('The remote server is unreachable')
    except ValueError:
        raise click.ClickException('You have probably mistaken value for an environment variable')


@cli.command('shell-completion')
@click.option('--append/--overwrite', help="Append the completion code to the file.", default=None)
@click.option('-i', 'case_insensitive', is_flag=True, default=False, help="Case insensitive completion.")
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
@click.argument('path', required=False)
def completion(append, case_insensitive, shell, path):
    """Installs shell completion. Supported shells are bash, fish, zsh and PowerShell."""
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    try:
        shell, path = click_completion.core.install(shell, path=path, append=append, extra_env=extra_env)
        click.secho(f'{shell} completion installed in {path}', fg='green')
    except OSError as e:
        raise click.ClickException(e)


cli.add_command(api_schema)
cli.add_command(available_objects)
cli.add_command(custom_request)
cli.add_command(resource)
