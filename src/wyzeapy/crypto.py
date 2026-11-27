#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import base64
import hashlib
import hmac
import urllib.parse
from typing import Dict, List, Union, Any

from .const import WEB_SIGNING_SECRET, FORD_APP_SECRET, OLIVE_SIGNING_SECRET

"""
Cryptographic helper functions for creating API request signatures.
"""

_XXTEA_DELTA = 0x9E3779B9


def _xxtea_to_uint32_list(data: bytes) -> List[int]:
    n = (len(data) + 3) >> 2
    result = [0] * n
    for i, byte in enumerate(data):
        result[i >> 2] |= byte << ((i & 3) << 3)
    return result


def _xxtea_to_bytes(v: List[int]) -> Union[bytes, None]:
    # The decrypted plaintext length is stored in the final word (the
    # "with length" XXTEA variant used by xxtea-js).
    n = (len(v) << 2) - 4
    m = v[-1]
    if m < n - 3 or m > n:
        return None
    out = bytearray(m)
    for i in range(m):
        out[i] = (v[i >> 2] >> ((i & 3) << 3)) & 0xFF
    return bytes(out)


def _xxtea_mx(s: int, y: int, z: int, p: int, e: int, k: List[int]) -> int:
    return (
        (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)))
        ^ ((s ^ y) + (k[(p & 3) ^ e] ^ z))
    ) & 0xFFFFFFFF


def xxtea_decrypt(data: bytes, key: bytes) -> Union[bytes, None]:
    """Decrypt XXTEA ciphertext, compatible with the xxtea-js library.

    Wyze's web app encrypts a camera's Agora stream key/salt this way,
    using the account access token as the key. Returns None if the
    ciphertext does not decode to a valid length.
    """
    if not data:
        return data
    if len(key) < 16:
        key = key + b"\x00" * (16 - len(key))
    v = _xxtea_to_uint32_list(data)
    k = _xxtea_to_uint32_list(key)
    n = len(v)
    last = n - 1
    y = v[0]
    s = (_XXTEA_DELTA * (6 + 52 // n)) & 0xFFFFFFFF
    while s != 0:
        e = (s >> 2) & 3
        for p in range(last, 0, -1):
            z = v[p - 1]
            v[p] = (v[p] - _xxtea_mx(s, y, z, p, e, k)) & 0xFFFFFFFF
            y = v[p]
        z = v[last]
        v[0] = (v[0] - _xxtea_mx(s, y, z, 0, e, k)) & 0xFFFFFFFF
        y = v[0]
        s = (s - _XXTEA_DELTA) & 0xFFFFFFFF
    return _xxtea_to_bytes(v)


def xxtea_decrypt_b64(value: str, key: str) -> Union[str, None]:
    """Decrypt a base64-encoded XXTEA string, returning UTF-8 text.

    Mirrors the web app's decryptFromBase64ToStr(value, token).
    """
    if not value or not key:
        return value
    decrypted = xxtea_decrypt(base64.b64decode(value), key.encode())
    return decrypted.decode() if decrypted is not None else None


def olive_create_signature(
    payload: Union[Dict[Any, Any], str], access_token: str
) -> str:
    """
    Compute the olive (Wyze) API request signature using HMAC-MD5.

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


def ford_create_signature(
    url_path: str, request_method: str, payload: Dict[Any, Any]
) -> str:
    """
    Compute the ford (Lock) API request signature using MD5 of URL-encoded buffer.

    Args:
        url_path: The URL path of the request.
        request_method: HTTP method (e.g., 'GET', 'POST').
        payload: The request payload dict to include in the signature.

    Returns:
        The computed signature as a hex string.
    """
    string_buf = request_method + url_path
    for entry in sorted(payload.keys()):
        string_buf += entry + "=" + payload[entry] + "&"

    string_buf = string_buf[:-1]
    string_buf += FORD_APP_SECRET
    urlencoded = urllib.parse.quote_plus(string_buf)
    return hashlib.md5(urlencoded.encode()).hexdigest()


def web_create_signature(payload: Union[Dict[Any, Any], str], access_token: str) -> str:
    """
    Compute the app (my.wyze.com) API request signature using HMAC-MD5.

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

    access_key = "{}{}".format(access_token, WEB_SIGNING_SECRET)

    secret = hashlib.md5(access_key.encode()).hexdigest()
    return hmac.new(secret.encode(), body.encode(), hashlib.md5).hexdigest()
