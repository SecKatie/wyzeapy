"""Utility functions for Wyzeapy."""

import hashlib
import hmac
import urllib.parse
from typing import Any, Dict, Union

# Crypto secrets for lock API
FORD_APP_KEY = "275965684684dbdaf29a0ed9"
FORD_APP_SECRET = "4deekof1ba311c5c33a9cb8e12787e8c"

# Olive (platform service) constants
OLIVE_SIGNING_SECRET = "wyze_app_secret_key_132"
OLIVE_APP_ID = "9319141212m2ik"
APP_INFO = "wyze_android_2.19.14"


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

    Args:
        payload: The request payload as a dict or raw string.
        access_token: The access token string for signing.

    Returns:
        The computed signature as a hex string.
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


class PropertyID:
    """Common property IDs for Wyze devices."""

    POWER = "P3"  # Power on/off
    BRIGHTNESS = "P1501"
    COLOR_TEMP = "P1502"
    COLOR = "P1507"
    COLOR_MODE = "P1508"  # 1=color, 2=white
    DOOR_OPEN = "P2001"
    CAMERA_SIREN = "P1049"
    MOTION_DETECTION = "P1047"
