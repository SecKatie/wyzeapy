#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from typing import List, Dict, Any

from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, DeviceTypes, PropertyIDs


class Switch(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)
        self.on: bool = False


class SwitchService(BaseService):
    async def update(self, switch: Switch):
        # Get updated device_params
        async with BaseService._update_lock:
            switch.device_params = await self.get_updated_params(switch.mac)

        device_info = await self._get_property_list(switch)

        for property_id, value in device_info:
            if property_id == PropertyIDs.ON:
                switch.on = value == "1"
            elif property_id == PropertyIDs.AVAILABLE:
                switch.available = value == "1"

        return switch

    async def get_switches(self) -> List[Switch]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        devices = [device for device in self._devices if device.type is DeviceTypes.PLUG or
                   device.type is DeviceTypes.OUTDOOR_PLUG]
        return [Switch(switch.raw_dict) for switch in devices]

    async def turn_on(self, switch: Switch):
        await self._set_property(switch, PropertyIDs.ON.value, "1")

    async def turn_off(self, switch: Switch):
        await self._set_property(switch, PropertyIDs.ON.value, "0")
