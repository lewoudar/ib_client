import click

from infoblox.exceptions import HttpError
from infoblox.scripts.utils import pretty_echo, handle_json_file, handle_json_arguments


@click.command('objects')
@click.pass_obj
def available_objects(obj):
    """List the available objects supports by the infoblox api."""
    pretty_echo(obj.client.available_objects)


@click.command('schema')
@click.pass_obj
def api_schema(obj):
    """Get the api schema."""
    pretty_echo(obj.client.api_schema)


@click.command('request')
@click.option('-j', 'json_file', type=click.Path(exists=True), callback=handle_json_file, is_eager=True,
              expose_value=False, help='json file which must contains the payload of the request')
@click.argument('json_data', nargs=-1, required=True, callback=handle_json_arguments)
@click.pass_obj
def custom_request(obj, json_data):
    """
    Makes a custom request using the request object of infoblox api.
    JSON_DATA: data which will be converted to dict and passed to Client.custom_request method.

    \b
    Examples usage:
    ib request '{"data": {"name": "test.somewhere.com"}, "method": "GET", "object": "record:host"}'
    ib request data:='{"name": "test.somewhere.com"}' method=GET object:='"record:host"'
    ib request -j foo.json  # where foo.json is the file containing the payload in json format.
    """
    try:
        pretty_echo(obj.client.custom_request(json_data))
    except HttpError as e:
        pretty_echo(e.error_message)
