#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import time

from .base_service import BaseService
from ..const import FORD_APP_SECRET
from ..types import Device, DeviceTypes
from ..utils import wyze_decrypt_cbc


LOCK_BOLT_V2_MODEL = "DX_LB2"


class Lock(Device):
    unlocked = False
    locking = False
    unlocking = False
    door_open = False
    trash_mode = False
    ble_id = None
    ble_token = None
    battery_level = None


class LockService(BaseService):

    async def _update_lock_bolt_v2(self, lock: Lock) -> Lock:
        """Update lock state for the Wyze Lock Bolt v2 (DX_LB2) using the
        devicemgmt IoT property API. Lock/unlock control is not yet supported
        for this model."""
        payload = {
            "capabilities": [
                {
                    "iid": 1,
                    "name": "iot-device",
                    "properties": ["iot-state", "push-switch"]
                },
                {
                    "iid": 2,
                    "name": "lock",
                    "properties": ["lock-status"]
                },
                {
                    "iid": 4,
                    "name": "battery",
                    "properties": ["battery-level", "power-source"]
                },
            ],
            "nonce": int(time.time() * 1000),
            "targetInfo": {
                "id": lock.mac,
                "productModel": lock.product_model,
                "type": "DEVICE",
            },
        }

        headers = {"authorization": self._auth_lib.token.access_token}

        response = await self._auth_lib.post(
            "https://devicemgmt-service-beta.wyze.com/device-management/api/device-property/get_iot_prop",
            json=payload,
            headers=headers,
        )

        capabilities = {
            cap["name"]: cap["properties"]
            for cap in response.get("data", {}).get("capabilities", [])
        }

        # Online state
        iot = capabilities.get("iot-device", {})
        lock.available = iot.get("iot-state", False)

        # Lock state: True = locked, False = unlocked
        lock_props = capabilities.get("lock", {})
        lock_status = lock_props.get("lock-status", True)
        lock.unlocked = not lock_status

        # Battery
        battery = capabilities.get("battery", {})
        lock.battery_level = battery.get("battery-level")

        # Reset in-progress states if they've completed
        if lock.unlocked and lock.unlocking:
            lock.unlocking = False
        if not lock.unlocked and lock.locking:
            lock.locking = False

        return lock

    async def update(self, lock: Lock) -> Lock:
        """Update lock state. Routes to the appropriate API based on model."""
        if lock.product_model == LOCK_BOLT_V2_MODEL:
            return await self._update_lock_bolt_v2(lock)

        # Original Ford API path for v1 locks
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

        locker_status = lock.raw_dict.get("locker_status")
        lock.unlocked = locker_status.get("hardlock") == 2

        if lock.unlocked and lock.unlocking:
            lock.unlocking = False
        if not lock.unlocked and lock.locking:
            lock.locking = False

        return lock

    async def get_locks(self):
        """Return all locks including Wyze Lock Bolt v2 devices."""
        if self._devices is None:
            self._devices = await self.get_object_list()

        locks = [
            device for device in self._devices
            if device.type is DeviceTypes.LOCK
            or device.type is DeviceTypes.LOCK_BOLT_V2
        ]

        return [Lock(device.raw_dict) for device in locks]

    async def lock(self, lock: Lock):
        """Lock the device. Not yet supported for Lock Bolt v2."""
        if lock.product_model == LOCK_BOLT_V2_MODEL:
            raise NotImplementedError(
                "Lock control is not yet supported for the Wyze Lock Bolt v2 (DX_LB2). "
                "State monitoring is available."
            )
        await self._lock_control(lock, "remoteLock")

    async def unlock(self, lock: Lock):
        """Unlock the device. Not yet supported for Lock Bolt v2."""
        if lock.product_model == LOCK_BOLT_V2_MODEL:
            raise NotImplementedError(
                "Unlock control is not yet supported for the Wyze Lock Bolt v2 (DX_LB2). "
                "State monitoring is available."
            )
        await self._lock_control(lock, "remoteUnlock")