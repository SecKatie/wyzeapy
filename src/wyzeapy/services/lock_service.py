#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from wyzeapy.payload_factory import ford_create_payload
from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, PropertyIDs, DeviceTypes
from wyzeapy.utils import check_for_errors_lock


class Lock(Device):
    unlocked = False
    door_open = False


class LockService(BaseService):
    async def update(self, lock: Lock):
        device_info = await self._get_info(lock)

        for property_id, value in device_info:
            if property_id == PropertyIDs.ON:
                lock.unlocked = value == "1"
            elif property_id == PropertyIDs.AVAILABLE:
                lock.available = value == "1"
            elif property_id == PropertyIDs.DOOR_OPEN:
                lock.door_open = value == "1"

        return lock

    async def get_locks(self):
        if self._devices is None:
            self._devices = await self._get_devices()

        locks = [device for device in self._devices if device.type is DeviceTypes.LOCK]

        return [Lock(device.raw_dict) for device in locks]

    async def lock(self, lock: Lock):
        await self._lock_control(lock, "remoteLock")

    async def unlock(self, lock: Lock):
        await self._lock_control(lock, "remoteUnlock")

    async def _lock_control(self, device: Device, action: str) -> None:
        await self._auth_lib.refresh_if_should()

        url_path = "/openapi/lock/v1/control"

        device_uuid = device.mac.split(".")[2]

        payload = {
            "uuid": device_uuid,
            "action": action  # "remoteLock" or "remoteUnlock"
        }
        payload = ford_create_payload(self._auth_lib.token.access_token, payload, url_path, "post")

        url = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/control"

        response_json = await self._auth_lib.post(url, json=payload)

        check_for_errors_lock(response_json)
