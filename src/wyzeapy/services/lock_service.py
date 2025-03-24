#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
from .base_service import BaseService
from ..const import FORD_APP_SECRET
from ..types import Device, DeviceTypes
from ..utils import wyze_decrypt_cbc


class Lock(Device):
    unlocked = False
    locking = False
    unlocking = False
    door_open = False
    trash_mode = False
    ble_id = None
    ble_token = None


class LockService(BaseService):
    async def update(self, lock: Lock):
        device_info = await self._get_lock_info(lock)
        lock.raw_dict = device_info["device"]
        if lock.product_model == "YD_BT1":
            ble_token_info = await self._get_lock_ble_token(lock)
            lock.raw_dict["token"] = ble_token_info["token"]
            lock.ble_id = ble_token_info["token"]["id"]
            lock.ble_token = wyze_decrypt_cbc(FORD_APP_SECRET[:16], ble_token_info["token"]["token"])

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
        if self._devices is None:
            self._devices = await self.get_object_list()

        locks = [device for device in self._devices if device.type is DeviceTypes.LOCK]

        return [Lock(device.raw_dict) for device in locks]

    async def lock(self, lock: Lock):
        await self._lock_control(lock, "remoteLock")

    async def unlock(self, lock: Lock):
        await self._lock_control(lock, "remoteUnlock")
