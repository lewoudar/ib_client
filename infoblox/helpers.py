import json

import requests

from .exceptions import BadParameterError, HttpError


def url_join(base_url: str, path: str) -> str:
    """
    :param base_url: base url.
    :param path: path to join to base url
    :return: the joined url.
    """
    for item in [base_url, path]:
        if not isinstance(item, str):
            raise BadParameterError(f'{item} is not a string')
    return f'{base_url.rstrip("/")}/{path.lstrip("/")}'


def handle_http_error(response: requests.Response) -> None:
    """Handles client and server errors."""
    if response.status_code >= 400:
        try:
            error_message = response.json()
        except json.JSONDecodeError:
            error_message = response.text
        raise HttpError(response.status_code, error_message)
