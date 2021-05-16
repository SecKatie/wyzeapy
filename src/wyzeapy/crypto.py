#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import hashlib
import hmac
import urllib.parse
from typing import Dict, Union

from .const import FORD_APP_SECRET, OLIVE_SIGNING_SECRET


def olive_create_signature(payload: Union[dict, str], access_token: str) -> str:
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


def ford_create_signature(url_path, request_method, payload: Dict):
    string_buf = request_method + url_path
    for entry in sorted(payload.keys()):
        string_buf += entry + "=" + payload[entry] + "&"

    string_buf = string_buf[:-1]
    string_buf += FORD_APP_SECRET
    urlencoded = urllib.parse.quote_plus(string_buf)
    return hashlib.md5(urlencoded.encode()).hexdigest()
