"""Additional click types used in the project"""
import json

import click


class StringListParamType(click.ParamType):
    """Converts a comma-separated list of strings and returns a list of strings."""
    name = 'string list'

    def convert(self, value, param, ctx):
        return value.split(',')


class JsonParamType(click.ParamType):
    """Converts a json string as input and returns a dict."""
    name = 'json'

    def convert(self, value, param, ctx):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            self.fail(f'{value} is not a valid json value', param, ctx)


STRING_LIST = StringListParamType()
DICT = JsonParamType()
