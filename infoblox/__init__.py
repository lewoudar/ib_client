__version__ = '0.1.0'

from .client import Client
from .resource import Resource
from .exceptions import (
    IBError, BadParameterError, HttpError, IncompatibleApiError, IncompatibleOperationError, MandatoryFieldError,
    FieldError, SearchOnlyFieldError, NotSearchableFieldError, NotFoundError, FileError, ObjectNotFoundError,
    FieldNotFoundError, FunctionNotFoundError
)
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
