#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import json
import random
import time
import uuid

from .base_service import BaseService
from ..const import FORD_APP_SECRET, OLIVE_APP_ID, PHONE_ID
from ..crypto import olive_create_signature
from ..exceptions import AccessTokenError, UnknownApiError
from ..types import Device, DeviceTypes, ResponseCodes
from ..utils import wyze_decrypt_cbc

# Some lock hardware (confirmed: DX_PVLOC, the Wyze Palm Lock; DX_LB2, the
# Wyze Lock Bolt 2) is reported by Wyze's cloud API with product_type
# "Common" instead of "Lock", and does not speak the Ford/Yunding lock
# protocol at all (calling /openapi/lock/v1/* fails with ErrNo 15501
# OPEN_AUTH_EMPTY regardless of uuid, because the device was never
# registered with Ford). These models only speak Wyze's separate "IoT3"
# API (/app/v4/iot3/get-property, /app/v4/iot3/run-action), reverse-engineered
# by the wyze-api Node project (https://github.com/jfarmer08/wyze-api), whose
# changelog confirms IoT3 support was added for both models together.
IOT3_LOCK_PRODUCT_MODELS = {"DX_PVLOC", "DX_LB2"}

IOT3_APP_INFO = "wyze_android_3.11.0.758"
IOT3_APP_VERSION = "3.11.0.758"
IOT3_BASE_URL = "https://app.wyzecam.com"


class Lock(Device):
    unlocked = False
    locking = False
    unlocking = False
    door_open = False
    trash_mode = False
    ble_id = None
    ble_token = None


def _check_for_errors_iot3(service, response_json) -> None:
    if str(response_json.get("code")) != ResponseCodes.SUCCESS.value:
        if str(response_json.get("code")) == ResponseCodes.ACCESS_TOKEN_ERROR.value:
            service._auth_lib.token.expired = True
            raise AccessTokenError("Access Token expired, attempting to refresh")
        raise UnknownApiError(response_json)


def _iot3_headers(body: str, access_token: str) -> dict:
    return {
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "myapp",
        "access_token": access_token,
        "appid": OLIVE_APP_ID,
        "appinfo": IOT3_APP_INFO,
        "appversion": IOT3_APP_VERSION,
        "env": "Prod",
        "phoneid": PHONE_ID,
        "requestid": uuid.uuid4().hex,
        "signature2": olive_create_signature(body, access_token),
    }


async def _iot3_get_properties(service, device: Device, props: list):
    await service._auth_lib.refresh_if_should()

    ts = int(time.time() * 1000)
    payload = {
        "nonce": str(ts),
        "payload": {
            "cmd": "get_property",
            "props": props,
            "tid": random.randint(10000, 98999),
            "ts": ts,
            "ver": 1,
        },
        "targetInfo": {"id": device.mac, "model": device.product_model},
    }
    body = json.dumps(payload, separators=(",", ":"))
    headers = _iot3_headers(body, service._auth_lib.token.access_token)

    response_json = await service._auth_lib.post(
        f"{IOT3_BASE_URL}/app/v4/iot3/get-property", headers=headers, data=body
    )

    _check_for_errors_iot3(service, response_json)

    return response_json


async def _iot3_run_action(service, device: Device, action: str):
    await service._auth_lib.refresh_if_should()

    ts = int(time.time() * 1000)
    payload = {
        "nonce": str(ts),
        "payload": {
            "action": action,
            "cmd": "run_action",
            "params": {
                "action_id": random.randint(10000, 99999),
                "type": 1,
                "username": service._auth_lib._username,
            },
            "tid": random.randint(10000, 98999),
            "ts": ts,
            "ver": 1,
        },
        "targetInfo": {"id": device.mac, "model": device.product_model},
    }
    body = json.dumps(payload, separators=(",", ":"))
    headers = _iot3_headers(body, service._auth_lib.token.access_token)

    response_json = await service._auth_lib.post(
        f"{IOT3_BASE_URL}/app/v4/iot3/run-action", headers=headers, data=body
    )

    _check_for_errors_iot3(service, response_json)

    return response_json


class LockService(BaseService):
    async def update(self, lock: Lock):
        if getattr(lock, "product_model", None) in IOT3_LOCK_PRODUCT_MODELS:
            response_json = await _iot3_get_properties(
                self,
                lock,
                [
                    "lock::lock-status",
                    "battery::battery-level",
                    "iot-device::iot-state",
                    "device-info::firmware-ver",
                ],
            )
            # data.props comes back as a flat {pid: value} dict with native
            # JSON types (bool/int/str) -- confirmed against the live API,
            # not documented anywhere.
            props = response_json.get("data", {}).get("props") or {}
            lock.raw_dict["power"] = props.get("battery::battery-level")
            lock.available = bool(props.get("iot-device::iot-state"))
            lock.unlocked = bool(props.get("lock::lock-status"))
            lock.door_open = False
            lock.trash_mode = False

            if lock.unlocked and lock.unlocking:
                lock.unlocking = False
            if not lock.unlocked and lock.locking:
                lock.locking = False

            return lock

        device_info = await self._get_lock_info(lock)
        lock.raw_dict = device_info["device"]
        if lock.product_model == "YD_BT1":
            ble_token_info = await self._get_lock_ble_token(lock)
            lock.raw_dict["token"] = ble_token_info["token"]
            lock.ble_id = ble_token_info["token"]["id"]
            lock.ble_token = wyze_decrypt_cbc(
                FORD_APP_SECRET[:16], ble_token_info["token"]["token"]
            )

        lock.available = lock.raw_dict.get("onoff_line") == 1
        lock.door_open = lock.raw_dict.get("door_open_status") == 1
        lock.trash_mode = lock.raw_dict.get("trash_mode") == 1

        # store the nested dict for easier reference below
        locker_status = lock.raw_dict.get("locker_status")
        # Check if the door is locked
        lock.unlocked = locker_status.get("hardlock") == 2

        # Reset unlocking and locking if needed
        if lock.unlocked and lock.unlocking:
            lock.unlocking = False
        if not lock.unlocked and lock.locking:
            lock.locking = False

        return lock

    async def get_locks(self):
        locks = [
            device
            for device in await self._get_cached_devices()
            if device.type is DeviceTypes.LOCK
            or getattr(device, "product_model", None) in IOT3_LOCK_PRODUCT_MODELS
        ]

        return [Lock(device.raw_dict) for device in locks]

    async def lock(self, lock: Lock):
        if getattr(lock, "product_model", None) in IOT3_LOCK_PRODUCT_MODELS:
            await _iot3_run_action(self, lock, "lock::lock")
            return
        await self._lock_control(lock, "remoteLock")

    async def unlock(self, lock: Lock):
        if getattr(lock, "product_model", None) in IOT3_LOCK_PRODUCT_MODELS:
            await _iot3_run_action(self, lock, "lock::unlock")
            return
        await self._lock_control(lock, "remoteUnlock")
