#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import time
from typing import List, Dict, Any

from wyzeapy.const import PHONE_SYSTEM_TYPE, APP_VERSION, APP_VER, PHONE_ID, APP_NAME
from wyzeapy.exceptions import ActionNotSupported
from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, DeviceTypes, PropertyIDs
from wyzeapy.utils import check_for_errors_standard


class Switch(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)
        self.on: bool = False


class SwitchService(BaseService):
    async def update(self, switch: Switch):
        device_info = await self._get_info(switch)

        for property_id, value in device_info:
            if property_id == PropertyIDs.ON:
                switch.on = value == "1"
            elif property_id == PropertyIDs.AVAILABLE:
                switch.available = value == "1"

        return switch

    async def get_switches(self) -> List[Switch]:
        if self._devices is None:
            self._devices = await self._get_devices()

        devices = [device for device in self._devices if device.type is DeviceTypes.PLUG or
                   device.type is DeviceTypes.OUTDOOR_PLUG]
        return [Switch(switch.raw_dict) for switch in devices]

    async def turn_on(self, switch: Device):
        if switch.type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            await self.set_property(switch, PropertyIDs.ON.value, "1")

    async def turn_off(self, switch: Device):
        if switch.type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            await self.set_property(switch, PropertyIDs.ON.value, "0")

    async def set_property(self, device: Device, pid: str, pvalue: str) -> None:
        """
        Sets a single property on the selected device.
        Only works for Plugs, Lights, and Outdoor Plugs

        :param device: Device
        :param pid: str
        :param pvalue: str
        :return: None
        """

        if self._auth_lib.should_refresh:
            await self._auth_lib.refresh()

        if DeviceTypes(device.product_type) not in [
            DeviceTypes.PLUG,
            DeviceTypes.LIGHT,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            raise ActionNotSupported(device.product_type)

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "pvalue": pvalue,
            "pid": pid,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/set_property",
                                                  json=payload)

        check_for_errors_standard(response_json)
