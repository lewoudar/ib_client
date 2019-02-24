import click
from click_didyoumean import DYMGroup

from infoblox.exceptions import ObjectNotFoundError, FieldNotFoundError, FunctionNotFoundError, HttpError, IBError
from .options import (
    return_fields_option, return_fields_plus_option, proxy_search_option, params_option, object_ref_option,
    schedule_time_option, schedule_now_option, schedule_predecessor_option, schedule_warn_level_option,
    approval_comment_option, approval_query_mode_option, approval_ticket_number_option, arguments_option
)
from .utils import pretty_echo


@click.group('object', cls=DYMGroup)
@click.option('-n', '--name', 'wapi_object', nargs=1, prompt='wapi object',
              help='Wapi object you want to interact with.')
@click.pass_obj
def resource(obj, wapi_object):
    """Performs various object operations."""
    try:
        obj.resource = obj.client.get_object(wapi_object)
    except ObjectNotFoundError as e:
        raise click.UsageError(e)


@resource.command()
@click.pass_obj
def documentation(obj):
    """Show object api documentation."""
    pretty_echo(obj.resource.documentation)


@resource.command()
@click.pass_obj
def fields(obj):
    """List all object fields."""
    pretty_echo(obj.resource.fields)


@resource.command()
@click.pass_obj
def functions(obj):
    """Lists all object functions."""
    pretty_echo(obj.resource.functions)


@resource.command('field-info')
@click.option('-n', '--name', prompt='field name', help='Name of the field whose information is required.')
@click.pass_obj
def get_field_information(obj, name):
    """Gets object's field information."""
    try:
        pretty_echo(obj.resource.get_field_information(name))
    except FieldNotFoundError as e:
        raise click.BadOptionUsage(name, e)


@resource.command('func-info')
@click.option('-n', '--name', prompt='function name', help='Name of the function whose information is required.')
@click.pass_obj
def get_function_information(obj, name):
    """Gets object's function information."""
    try:
        pretty_echo(obj.resource.get_function_information(name))
    except FunctionNotFoundError as e:
        raise click.BadOptionUsage(name, e)


@resource.command()
# We don't use custom object_ref_option because object_ref is not required here (no prompt is necessary)
@click.option('-o', '--object-ref', help='Reference of the object to fetch.')
@params_option
@return_fields_option
@return_fields_plus_option
@proxy_search_option
@click.pass_obj
def get(obj, object_ref=None, params=None, return_fields=None, return_fields_plus=None, proxy_search=None):
    """Performs HTTP GET operations to search objects."""
    try:
        pretty_echo(obj.resource.get(object_ref, params, return_fields, return_fields_plus, proxy_search))
    except HttpError as e:
        pretty_echo(e.error_message)
    except IBError as e:
        raise click.UsageError(e)


@resource.command(short_help='Counts infoblox objects.')
@params_option
@proxy_search_option
@click.pass_obj
def count(obj, params=None, proxy_search=None):
    """
    Counts and returns the number of objects corresponding to giving parameters.
    """
    try:
        pretty_echo(obj.resource.count(params, proxy_search))
    except HttpError as e:
        pretty_echo(e.error_message)
    except IBError as e:
        raise click.UsageError(e)


@resource.command('func-call', short_help='Calls a function of an infoblox object.')
# We don't use custom object_ref_option because object_ref is not required here (no prompt is necessary)
@click.option('-o', '--object-ref', help='Reference of the object to fetch.', default=None)
@click.option('-n', '--name', prompt='function name', help='Name of the function to call.')
@arguments_option
@click.pass_obj
def function_call(obj, object_ref, name, arguments):
    """Performs a function call of an object which reference is specified in input."""
    try:
        pretty_echo(obj.resource.func_call(object_ref, name, **arguments))
    except HttpError as e:
        pretty_echo(e.error_message)
    except IBError as e:
        raise click.UsageError(e)


@resource.command()
@schedule_time_option
@schedule_now_option
@schedule_predecessor_option
@schedule_warn_level_option
@approval_comment_option
@approval_query_mode_option
@approval_ticket_number_option
@return_fields_option
@return_fields_plus_option
@arguments_option
@click.pass_obj
def create(obj, schedule_time=None, schedule_now=None, predecessor_task=None, warn_level=None, approval_comment=None,
           query_mode=None, ticket_number=None, return_fields=None, return_fields_plus=None, arguments=None):
    """Creates an infoblox object."""
    try:
        response = obj.resource.create(schedule_time, schedule_now, predecessor_task, warn_level, approval_comment,
                                       query_mode, ticket_number, return_fields, return_fields_plus, **arguments)
        pretty_echo(response)
    except HttpError as e:
        pretty_echo(e.error_message)
    except IBError as e:
        raise click.UsageError(e)


@resource.command()
@object_ref_option
@schedule_time_option
@schedule_now_option
@schedule_predecessor_option
@schedule_warn_level_option
@approval_comment_option
@approval_query_mode_option
@approval_ticket_number_option
@return_fields_option
@return_fields_plus_option
@arguments_option
@click.pass_obj
def update(obj, object_ref=None, schedule_time=None, schedule_now=None, predecessor_task=None, warn_level=None,
           approval_comment=None, query_mode=None, ticket_number=None, return_fields=None, return_fields_plus=None,
           arguments=None):
    """Updates an infoblox object given its reference."""
    try:
        response = obj.resource.update(object_ref, schedule_time, schedule_now, predecessor_task, warn_level,
                                       approval_comment, query_mode, ticket_number, return_fields, return_fields_plus,
                                       **arguments)
        pretty_echo(response)
    except HttpError as e:
        pretty_echo(e.error_message)
    except IBError as e:
        raise click.UsageError(e)


@resource.command()
@object_ref_option
@schedule_time_option
@schedule_now_option
@schedule_predecessor_option
@schedule_warn_level_option
@approval_comment_option
@approval_query_mode_option
@approval_ticket_number_option
@click.pass_obj
def delete(obj, object_ref=None, schedule_time=None, schedule_now=None, predecessor_task=None, warn_level=None,
           approval_comment=None, query_mode=None, ticket_number=None):
    """Deletes an infoblox object given its reference."""
    try:
        response = obj.resource.delete(object_ref, schedule_time, schedule_now, predecessor_task, warn_level,
                                       approval_comment, query_mode, ticket_number)
        pretty_echo(response)
    except HttpError as e:
        pretty_echo(e.error_message)
    except IBError as e:
        raise click.UsageError(e)
