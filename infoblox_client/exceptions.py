class IBError(Exception):
    """Base error."""
    pass


class BadParameterError(IBError):
    pass


class HttpError(IBError):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message


class IncompatibleApiError(IBError):
    pass


class SearchOnlyFieldError(BadParameterError):
    pass


class UnknownReturnTypeError(BadParameterError):
    pass


class FieldError(BadParameterError):
    pass


class NotFoundError(IBError):
    pass


class ObjectNotFoundError(NotFoundError):
    pass


class FieldNotFoundError(NotFoundError, FieldError):
    pass


class FunctionNotFoundError(NotFoundError):
    pass
