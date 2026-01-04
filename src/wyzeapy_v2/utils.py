"""Utility functions for Wyzeapy."""

import hashlib
import urllib.parse

# Crypto secrets for lock API
FORD_APP_KEY = "275965684684dbdaf29a0ed9"
FORD_APP_SECRET = "4deekof1ba311c5c33a9cb8e12787e8c"


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
