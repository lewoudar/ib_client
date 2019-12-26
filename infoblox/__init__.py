__version__ = '0.1.4.dev'

from .client import Client
from .exceptions import (
    IBError, BadParameterError, HttpError, IncompatibleApiError, IncompatibleOperationError, MandatoryFieldError,
    FieldError, SearchOnlyFieldError, NotSearchableFieldError, NotFoundError, FileError, ObjectNotFoundError,
    FieldNotFoundError, FunctionNotFoundError
)
from .resource import Resource
from .scripts.utils import pretty_echo, handle_json_arguments, parse_dict_items, handle_json_file

__all__ = [
    # core classes
    'Client', 'Resource',

    # exceptions
    'IBError', 'BadParameterError', 'HttpError', 'IncompatibleApiError', 'IncompatibleOperationError',
    'MandatoryFieldError', 'FieldError', 'SearchOnlyFieldError', 'NotSearchableFieldError', 'NotFoundError',
    'FileError', 'ObjectNotFoundError', 'FieldNotFoundError', 'FunctionNotFoundError',

    # script utilities
    'pretty_echo', 'handle_json_file', 'handle_json_arguments', 'parse_dict_items',
]
