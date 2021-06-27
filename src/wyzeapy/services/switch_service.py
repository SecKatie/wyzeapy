#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from typing import List

from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, DeviceTypes, PropertyIDs


class Switch(Device):
    pass


class SwitchService(BaseService):
    async def update(self, switch: Switch):
        device_info = await self._client.get_info(switch)

        for property_id, value in device_info:
            if property_id == PropertyIDs.ON:
                switch.on = value == "1"
            elif property_id == PropertyIDs.AVAILABLE:
                switch.available = value == "1"

        return switch

    async def get_switches(self) -> List[Switch]:
        return [Switch(switch.raw_dict) for switch in await self._client.get_plugs()]

    async def turn_on(self, switch: Device):
        if switch.type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            await self._client.net_client.set_property(switch, PropertyIDs.ON.value, "1")

    async def turn_off(self, switch: Device):
        if switch.type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            await self._client.net_client.set_property(switch, PropertyIDs.ON.value, "0")
