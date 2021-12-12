#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import re
from typing import Any, Dict, Optional, List

from .base_service import BaseService
from ..types import Device, PropertyIDs, DeviceTypes
from ..utils import create_pid_pair

_LOGGER = logging.getLogger(__name__)


class Bulb(Device):
    _brightness: int = 0
    _color_temp: int = 1800
    _color: Optional[str]
    enr: str

    on: bool = False

    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.ip = self.device_params["ip"]

        if self.type is DeviceTypes.MESH_LIGHT:
            self._color = "000000"

    @property
    def brightness(self) -> int:
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        assert value <= 100
        assert value >= 0
        self._brightness = value

    @property
    def color_temp(self) -> int:
        return self._color_temp

    @color_temp.setter
    def color_temp(self, value: int) -> None:
        self._color_temp = value

    @property
    def color(self) -> Optional[str]:
        return self._color

    @color.setter
    def color(self, value) -> None:
        assert re.match(r"^([A-Fa-f\d]{6}|[A-Fa-f\d]{3})$", value) is not None
        self._color = value


class BulbService(BaseService):
    async def update(self, bulb: Bulb) -> Bulb:
        # Get updated device_params
        async with BaseService._update_lock:
            bulb.device_params = await self.get_updated_params(bulb.mac)

        device_info = await self._get_property_list(bulb)
        for property_id, value in device_info:
            if property_id == PropertyIDs.BRIGHTNESS:
                bulb.brightness = int(float(value))
            elif property_id == PropertyIDs.COLOR_TEMP:
                try:
                    bulb.color_temp = int(value)
                except ValueError:
                    bulb.color_temp = 2700
            elif property_id == PropertyIDs.ON:
                bulb.on = value == "1"
            elif property_id == PropertyIDs.AVAILABLE:
                bulb.available = value == "1"
            elif bulb.type is DeviceTypes.MESH_LIGHT and property_id == PropertyIDs.COLOR:
                bulb.color = value
        return bulb

    async def get_bulbs(self) -> List[Bulb]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        bulbs = [device for device in self._devices if device.type is DeviceTypes.LIGHT or
                 device.type is DeviceTypes.MESH_LIGHT]

        return [Bulb(bulb.raw_dict) for bulb in bulbs]

    async def turn_on(self, bulb: Bulb, options=None):
        plist = [
            create_pid_pair(PropertyIDs.ON, "1")
        ]
        if options is not None:
            plist.extend(options)

        if bulb.type in [
            DeviceTypes.LIGHT
        ]:
            await self._set_property_list(bulb, plist)
        elif bulb.type in [
            DeviceTypes.MESH_LIGHT
        ]:
            await self._local_bulb_command(bulb, plist)

    async def turn_off(self, bulb: Bulb):
        plist = [
            create_pid_pair(PropertyIDs.ON, "0")
        ]

        if bulb.type in [
            DeviceTypes.LIGHT
        ]:
            await self._set_property_list(bulb, plist)
        elif bulb.type in [
            DeviceTypes.MESH_LIGHT
        ]:
            await self._local_bulb_command(bulb, plist)

    async def set_color_temp(self, bulb: Bulb, color_temp: int):
        plist = [
            create_pid_pair(PropertyIDs.COLOR_TEMP, str(color_temp))
        ]

        if bulb.type in [
            DeviceTypes.LIGHT
        ]:
            await self._set_property_list(bulb, plist)
        elif bulb.type in [
            DeviceTypes.MESH_LIGHT
        ]:
            await self._local_bulb_command(bulb, plist)

    async def set_color(self, bulb: Bulb, color: str):
        plist = [
            create_pid_pair(PropertyIDs.COLOR, str(color))
        ]

        if bulb.type in [
            DeviceTypes.MESH_LIGHT
        ]:
            await self._local_bulb_command(bulb, plist)

    async def set_brightness(self, bulb: Device, brightness: int):
        plist = [
            create_pid_pair(PropertyIDs.BRIGHTNESS, str(brightness))
        ]

        if bulb.type in [
            DeviceTypes.LIGHT
        ]:
            await self._set_property_list(bulb, plist)
        if bulb.type in [
            DeviceTypes.MESH_LIGHT
        ]:
            await self._local_bulb_command(bulb, plist)
