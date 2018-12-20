import os
import json
from typing import Any, Sequence, Optional

import click
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name
from pygments import highlight

from infoblox.exceptions import HttpError

DELIMITERS = ('=', ':=')
JSON_ERROR_MESSAGE = 'unable to parse json data, this input is not correct: {}'


def pretty_echo(data: Any) -> None:
    """Returns formatted and colored output on console."""
    json_lexer = get_lexer_by_name('json')
    console_formatter = get_formatter_by_name('console')
    click.echo(highlight(json.dumps(data, indent=4), json_lexer, console_formatter))


# noinspection PyUnusedLocal
def handle_json_file(context: click.Context, param: click.Parameter, json_file: str) -> None:
    """
    Gets dict from json_file, executes Client.custom_request method and exits program.
    :param context: click current context.
    :param param: current command parameter.
    :param json_file: json file representing payload data.
    """
    if not json_file or context.resilient_parsing:
        return
    try:
        with click.open_file(json_file) as f:
            info = json.load(f)
        pretty_echo(context.obj.client.custom_request(info))
    except json.JSONDecodeError:
        raise click.BadParameter(f'{json_file} is not a valid json file')
    except HttpError as e:
        pretty_echo(e.error_message)
    context.exit()


def _get_delimiter(item: str) -> Optional[str]:
    """
    Returns the delimiter found in the item if any. It may raises an error if delimiter starts or ends
    and item or if there is more than one delimiter in the item.
    :param item: the item to determine delimiters.
    """
    delimiters = (':=', '=')
    for delimiter in delimiters:
        if delimiter in item:
            if item.startswith(delimiter) or item.endswith(delimiter):
                raise click.UsageError(f'{delimiter} must not starts or ends an item like in {item}')
            if item.count(delimiter) > 1:
                raise click.UsageError(f'{item} contains more than one occurrence of {delimiter}')
            return delimiter


def _parse_item(item: str) -> dict:
    """
    Parses a string and returns a dict where key and value are extracted from string.
    For example, given an item "foo=bar" a dict with {'foo': 'bar'} will be returned or
    given "foo:=2" a dict with {'foo': 2} will be returned.
    :param item: the item to parse.
    """
    delimiter = _get_delimiter(item)
    key, value = item.split(delimiter)
    if delimiter == '=':
        return {key: value}
    else:
        try:
            return {key: json.loads(value)}
        except json.JSONDecodeError:
            raise click.UsageError(JSON_ERROR_MESSAGE.format(item))


def parse_dict_items(data: Sequence[str]) -> dict:
    """Parse arguments and returns a dict with all arguments"""
    info = {}
    # if there is only one element, it may contains a fully "jsonified" string
    # or an item of a dict
    if len(data) == 1:
        delimiter = _get_delimiter(data[0])
        if delimiter is None:
            try:
                return json.loads(data[0])
            except json.JSONDecodeError:
                raise click.UsageError(JSON_ERROR_MESSAGE.format(data[0]))
        else:
            return _parse_item(data[0])
    for item in data:
        info.update(_parse_item(item))
    return info


# noinspection PyUnusedLocal
def handle_json_arguments(context: click.Context, param: click.Parameter, items: Sequence[str]) -> Optional[dict]:
    """
    Assembles the input dictionary elements into a single dictionary and returns it
    :param context: click current context.
    :param param: current command parameter.
    :param items: dict items collecting as a tuple.
    """
    if not items or context.resilient_parsing:
        return
    return parse_dict_items(items)


def check_environment() -> None:
    """Check initialization of environment variables to configure cli."""
    for item in ['IB_USER', 'IB_PASSWORD', 'IB_URL']:
        if os.getenv(item) is None:
            raise click.UsageError(f'{item} environment variable must be set before using ib.')
