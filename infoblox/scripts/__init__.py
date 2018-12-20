import click

# noinspection PyProtectedMember
from infoblox import __version__, Client, Resource
from infoblox.scripts.client_commands import api_schema, available_objects, custom_request
from infoblox.scripts.resource_commands import resource
from infoblox.scripts.utils import check_environment

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.version_option(__version__)
@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(context):
    """
    Infoblox Command Line Interface. It allows you to interact with infoblox in the same way
    you will do with the python api client.
    """
    check_environment()

    class Container:
        def __init__(self):
            self.client = Client()
            self.resource: Resource = None

    context.obj = Container()


cli.add_command(api_schema)
cli.add_command(available_objects)
cli.add_command(custom_request)
cli.add_command(resource)
