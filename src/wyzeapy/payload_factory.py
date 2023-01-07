#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import time
from typing import Any, Dict

from .const import FORD_APP_KEY
from .crypto import ford_create_signature


def ford_create_payload(access_token: str, payload: Dict[str, Any],
                        url_path: str, request_method: str) -> Dict[str, Any]:
    payload["access_token"] = access_token
    payload["key"] = FORD_APP_KEY
    payload["timestamp"] = str(int(time.time() * 1000))
    payload["sign"] = ford_create_signature(url_path, request_method, payload)
    return payload


def olive_create_get_payload(device_mac: str, keys: str) -> Dict[str, Any]:
    nonce = int(time.time() * 1000)

    return {
        'keys': keys,
        'did': device_mac,
        'nonce': nonce
    }


def olive_create_post_payload(device_mac: str, device_model: str, prop_key: str, value: Any) -> Dict[str, Any]:
    nonce = int(time.time() * 1000)

    return {
        "did": device_mac,
        "model": device_model,
        "props": {
            prop_key: value
        },
        "is_sub_device": 0,
        "nonce": str(nonce)
    }


def olive_create_hms_payload() -> Dict[str, str]:
    nonce = int(time.time() * 1000)

    return {
        "group_id": "hms",
        "nonce": str(nonce)
    }


def olive_create_user_info_payload() -> Dict[str, str]:
    nonce = int(time.time() * 1000)

    return {
        "nonce": str(nonce)
    }


def olive_create_hms_get_payload(hms_id: str) -> Dict[str, str]:
    nonce = int(time.time() * 1000)
    return {
        "hms_id": hms_id,
        "nonce": str(nonce)
    }


def olive_create_hms_patch_payload(hms_id: str) -> Dict[str, Any]:
    return {
        "hms_id": hms_id
    }
