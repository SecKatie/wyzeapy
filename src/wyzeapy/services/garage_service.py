from typing import Any, Dict
from .base_service import BaseService
from ..types import Device, DeviceTypes

class GarageDoor(Device):
    open = False
    closing = False
    opening = False

class GarageService(BaseService):
    async def update(self, garage: GarageDoor):
        async with BaseService._update_lock:
            garage.device_params = await self.get_updated_params(garage.mac) 

        device_info = await self._get_device_info(garage)
        garage.raw_dict = device_info

        garage.available = True

        # store the nested dict for easier reference below
        property_list = await self._get_property_list(garage)
        for property in property_list:
            if property[0] == "P1056":
                garage.open = property[1] != "0"
                if garage.open and garage.opening:
                    garage.opening = False
                if not garage.open and garage.closing:
                    garage.closing = False
                break

        return garage

    async def get_garages(self):
        if self._devices is None:
            self._devices = await self.get_object_list()
        
        garages = [device for device in self._devices if device.type is DeviceTypes.GARAGE_DOOR]

        return [GarageDoor(device.raw_dict) for device in garages]

    async def open(self, garage: GarageDoor):
        if garage.open:
            return
        await self._run_action(garage, "garage_door_trigger")
        self.opening = True

    async def close(self, garage: GarageDoor):
        if not garage.open:
            return
        await self._run_action(garage, "garage_door_trigger")
        self.closing = True


