#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, PropertyIDs, DeviceTypes


class Lock(Device):
    unlocked = False
    door_open = False


class LockService(BaseService):
    async def update(self, lock: Lock):
        device_info = await self._get_property_list(lock)

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
            self._devices = await self.get_object_list()

        locks = [device for device in self._devices if device.type is DeviceTypes.LOCK]

        return [Lock(device.raw_dict) for device in locks]

    async def lock(self, lock: Lock):
        await self._lock_control(lock, "remoteLock")

    async def unlock(self, lock: Lock):
        await self._lock_control(lock, "remoteUnlock")
