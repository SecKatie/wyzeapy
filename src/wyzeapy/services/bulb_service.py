#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import logging
import re
from typing import Any, Dict, Optional, List

from .base_service import BaseService
from ..types import Device, PropertyIDs, DeviceTypes
from ..utils import create_pid_pair

_LOGGER = logging.getLogger(__name__)


class Bulb(Device):
    """Bulb class for interacting with Wyze bulbs."""

    _brightness: int = 0
    _color_temp: int = 1800
    _color: Optional[str]

    def __init__(self, dictionary: Dict[Any, Any]):
        """Initialize the Bulb class.

        :param dictionary: Dictionary containing the device parameters.
        """
        self.enr: str = ""
        """Encryption string"""
        self.on: bool = False
        """Variable that stores the on/off state of the bulb"""
        self.cloud_fallback: bool = False
        """Variable that stores the cloud fallback state of the bulb"""
        super().__init__(dictionary)

        self.ip = self.device_params["ip"]
        """IP address of the bulb"""

        if self.type is DeviceTypes.MESH_LIGHT or self.type is DeviceTypes.LIGHTSTRIP:
            self._color = "000000"

    @property
    def brightness(self) -> int:
        """Property that stores the brightness of the bulb
        :return: Brightness of the bulb
        """
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        """Setter for the brightness property
        :param value: Brightness of the bulb
        """
        assert value <= 100
        assert value >= 0
        self._brightness = value

    @property
    def color_temp(self) -> int:
        """Property that stores the color temperature of the bulb
        :return: Color temperature of the bulb
        """
        return self._color_temp

    @color_temp.setter
    def color_temp(self, value: int) -> None:
        """Setter for the color temperature property
        :param value: Color temperature of the bulb
        """
        self._color_temp = value

    @property
    def color(self) -> Optional[str]:
        """Property that stores the color of the bulb
        :return: Color of the bulb
        """
        return self._color

    @color.setter
    def color(self, value) -> None:
        """Setter for the color property
        :param value: Color of the bulb
        """
        assert re.match(r"^([A-Fa-f\d]{6}|[A-Fa-f\d]{3})$", value) is not None
        self._color = value


class BulbService(BaseService):
    """Bulb service for interacting with Wyze bulbs."""

    async def update(self, bulb: Bulb) -> Bulb:
        """Update the bulb object with the latest device parameters.

        :param bulb: Bulb object to update
        :return: Updated bulb object
        """
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
            elif property_id == PropertyIDs.COLOR and bulb.type in [
                DeviceTypes.LIGHTSTRIP,
                DeviceTypes.MESH_LIGHT,
            ]:
                bulb.color = value
            elif property_id == PropertyIDs.COLOR_MODE:
                bulb.color_mode = value
            elif property_id == PropertyIDs.SUN_MATCH:
                bulb.sun_match = value == "1"
            elif property_id == PropertyIDs.LIGHTSTRIP_EFFECTS:
                bulb.effects = value
            elif property_id == PropertyIDs.LIGHTSTRIP_MUSIC_MODE:
                bulb.music_mode = value == "1"

        return bulb

    async def get_bulbs(self) -> List[Bulb]:
        """Get a list of all bulbs.

        :return: List of Bulb objects
        """
        if self._devices is None:
            self._devices = await self.get_object_list()

        bulbs = [
            device
            for device in self._devices
            if device.type
            in [DeviceTypes.LIGHT, DeviceTypes.MESH_LIGHT, DeviceTypes.LIGHTSTRIP]
        ]

        return [Bulb(bulb.raw_dict) for bulb in bulbs]

    async def turn_on(self, bulb: Bulb, local_control, options=None):
        plist = [create_pid_pair(PropertyIDs.ON, "1")]

        if options is not None:
            plist.extend(options)

        if bulb.type is DeviceTypes.LIGHT:
            await self._set_property_list(bulb, plist)

        elif bulb.type in [DeviceTypes.MESH_LIGHT, DeviceTypes.LIGHTSTRIP]:
            # Local Control
            if local_control and not bulb.cloud_fallback:
                await self._local_bulb_command(bulb, plist)

            # Cloud Control
            elif (
                bulb.type is DeviceTypes.MESH_LIGHT
            ):  # Sun match for mesh bulbs needs to be set on a different endpoint for some reason
                for item in plist:
                    if item["pid"] == PropertyIDs.SUN_MATCH.value:
                        await self._set_property_list(bulb, [item])
                        plist.remove(item)
                await self._run_action_list(bulb, plist)
            else:
                await self._run_action_list(bulb, plist)  # Lightstrips

    async def turn_off(self, bulb: Bulb, local_control):
        plist = [create_pid_pair(PropertyIDs.ON, "0")]

        if bulb.type in [DeviceTypes.LIGHT]:
            await self._set_property_list(bulb, plist)
        elif bulb.type in [DeviceTypes.MESH_LIGHT, DeviceTypes.LIGHTSTRIP]:
            if local_control and not bulb.cloud_fallback:
                await self._local_bulb_command(bulb, plist)
            else:
                await self._run_action_list(bulb, plist)

    async def set_color_temp(self, bulb: Bulb, color_temp: int):
        plist = [create_pid_pair(PropertyIDs.COLOR_TEMP, str(color_temp))]

        if bulb.type in [DeviceTypes.LIGHT]:
            await self._set_property_list(bulb, plist)
        elif bulb.type in [DeviceTypes.MESH_LIGHT]:
            await self._local_bulb_command(bulb, plist)

    async def set_color(self, bulb: Bulb, color: str, local_control):
        plist = [create_pid_pair(PropertyIDs.COLOR, str(color))]
        if bulb.type in [DeviceTypes.MESH_LIGHT]:
            if local_control and not bulb.cloud_fallback:
                await self._local_bulb_command(bulb, plist)
            else:
                await self._run_action_list(bulb, plist)

    async def set_brightness(self, bulb: Device, brightness: int):
        plist = [create_pid_pair(PropertyIDs.BRIGHTNESS, str(brightness))]

        if bulb.type in [DeviceTypes.LIGHT]:
            await self._set_property_list(bulb, plist)
        if bulb.type in [DeviceTypes.MESH_LIGHT]:
            await self._local_bulb_command(bulb, plist)

    async def music_mode_on(self, bulb: Device):
        plist = [create_pid_pair(PropertyIDs.LIGHTSTRIP_MUSIC_MODE, "1")]

        await self._run_action_list(bulb, plist)

    async def music_mode_off(self, bulb: Device):
        plist = [create_pid_pair(PropertyIDs.LIGHTSTRIP_MUSIC_MODE, "0")]

        await self._run_action_list(bulb, plist)
