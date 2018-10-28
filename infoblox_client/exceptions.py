class IBError(Exception):
    """Base error."""
    pass


class BadParameterError(IBError):
    pass


class HttpError(IBError):
    pass


class IncompatibleApiError(IBError):
    pass


class SearchOnlyFieldError(IBError):
    pass


class NotFoundError(IBError):
    pass


class ObjectNotFoundError(NotFoundError):
    pass


class FieldNotFoundError(NotFoundError):
    pass


class FunctionNotFoundError(NotFoundError):
    pass
