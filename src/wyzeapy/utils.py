"""Utility functions for Wyzeapy."""

import hashlib
import hmac
import urllib.parse
from typing import Any, Dict, TypeVar, Union, overload

from .wyze_api_client.types import UNSET, Unset
from .const import (
    FORD_APP_KEY,
    FORD_APP_SECRET,
    OLIVE_SIGNING_SECRET,
    OLIVE_APP_ID,
    APP_INFO,
    PropertyID,
    DEVICEMGMT_API_MODELS,
    DEVICEMGMT_SERVICE_URL,
)

# Re-export for backwards compatibility
__all__ = [
    "hash_password",
    "ford_create_signature",
    "olive_create_signature",
    "is_set",
    "get_or_default",
    "FORD_APP_KEY",
    "FORD_APP_SECRET",
    "OLIVE_SIGNING_SECRET",
    "OLIVE_APP_ID",
    "APP_INFO",
    "PropertyID",
    "DEVICEMGMT_API_MODELS",
    "DEVICEMGMT_SERVICE_URL",
]

T = TypeVar("T")


def is_set(value: T | Unset) -> bool:
    """Check if a value is set (not Unset)."""
    return not isinstance(value, Unset)


@overload
def get_or_default(value: T | Unset, default: T) -> T: ...


@overload
def get_or_default(value: T | Unset, default: None = None) -> T | None: ...


def get_or_default(value: T | Unset, default: T | None = None) -> T | None:
    """
    Get the value if set, otherwise return the default.

    :param value: A value that may be Unset.
    :param default: Default value to return if value is Unset.
    :returns: The value if set, otherwise the default.
    """
    if isinstance(value, Unset):
        return default
    return value


def hash_password(password: str) -> str:
    """Triple MD5 hash the password as required by Wyze API."""
    for _ in range(3):
        password = hashlib.md5(password.encode()).hexdigest()
    return password


def ford_create_signature(url_path: str, request_method: str, payload: dict) -> str:
    """Create signature for lock API requests."""
    string_buf = request_method + url_path
    for entry in sorted(payload.keys()):
        string_buf += entry + "=" + str(payload[entry]) + "&"
    string_buf = string_buf[:-1]
    string_buf += FORD_APP_SECRET
    urlencoded = urllib.parse.quote_plus(string_buf)
    return hashlib.md5(urlencoded.encode()).hexdigest()


def olive_create_signature(
    payload: Union[Dict[Any, Any], str], access_token: str
) -> str:
    """
    Create signature for olive (platform service) API requests using HMAC-MD5.

    :param payload: The request payload as a dict or raw string.
    :type payload: Union[Dict[Any, Any], str]
    :param access_token: The access token string for signing.
    :type access_token: str
    :returns: The computed signature as a hex string.
    :rtype: str
    """
    if isinstance(payload, dict):
        body = ""
        for item in sorted(payload):
            body += item + "=" + str(payload[item]) + "&"
        body = body[:-1]
    else:
        body = payload

    access_key = "{}{}".format(access_token, OLIVE_SIGNING_SECRET)
    secret = hashlib.md5(access_key.encode()).hexdigest()
    return hmac.new(secret.encode(), body.encode(), hashlib.md5).hexdigest()
