#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
from enum import Enum
from typing import Any, Dict, List

from .base_service import BaseService
from ..types import Device, WallSwitchProps, DeviceTypes

_LOGGER = logging.getLogger(__name__)


class SinglePressType(Enum):
    CLASSIC = 1
    IOT = 2


class WallSwitch(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.switch_power: bool = False
        self.switch_iot: bool = False
        self.single_press_type: SinglePressType = SinglePressType.CLASSIC

    @property
    def on(self):
        if self.single_press_type == SinglePressType.IOT:
            return self.switch_iot
        return self.switch_power

    @on.setter
    def on(self, state: bool):
        if self.single_press_type == SinglePressType.IOT:
            self.switch_iot = state
        self.switch_power = state


class WallSwitchService(BaseService):
    async def update(self, switch: WallSwitch) -> WallSwitch:
        properties = (await self._wall_switch_get_iot_prop(switch))['data']['props']

        device_props = []
        for prop_key, prop_value in properties.items():
            try:
                prop = WallSwitchProps(prop_key)
                device_props.append((prop, prop_value))
            except ValueError as e:
                _LOGGER.debug(f"{e} with value {prop_value}")

        for prop, value in device_props:
            if prop == WallSwitchProps.IOT_STATE:
                switch.available = value == "connected"
            elif prop == WallSwitchProps.SWITCH_POWER:
                switch.switch_power = value
            elif prop == WallSwitchProps.SWITCH_IOT:
                switch.switch_iot = value
            elif prop == WallSwitchProps.SINGLE_PRESS_TYPE:
                switch.single_press_type = SinglePressType(value)

        return switch

    async def get_switches(self) -> List[WallSwitch]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        switches = [device for device in self._devices
                    if device.type is DeviceTypes.COMMON 
                    and device.product_model == "LD_SS1"]

        return [WallSwitch(switch.raw_dict) for switch in switches]

    async def turn_on(self, switch: WallSwitch):
        logging.warn("%s", switch.single_press_type)
        if switch.single_press_type == SinglePressType.IOT:
            await self.iot_on(switch)
        else:
            await self.power_on(switch)

    async def turn_off(self, switch: WallSwitch):
        if switch.single_press_type == SinglePressType.IOT:
            await self.iot_off(switch)
        else:
            await self.power_off(switch)

    async def power_on(self, switch: WallSwitch):
        await self._wall_switch_set_iot_prop(switch, WallSwitchProps.SWITCH_POWER, True)

    async def power_off(self, switch: WallSwitch):
        await self._wall_switch_set_iot_prop(switch, WallSwitchProps.SWITCH_POWER, False)

    async def iot_on(self, switch: WallSwitch):
        await self._wall_switch_set_iot_prop(switch, WallSwitchProps.SWITCH_IOT, True)

    async def iot_off(self, switch: WallSwitch):
        await self._wall_switch_set_iot_prop(switch, WallSwitchProps.SWITCH_IOT, False)

    async def set_single_press_type(self, switch: WallSwitch, single_press_type: SinglePressType):
        await self._wall_switch_set_iot_prop(switch, WallSwitchProps.SINGLE_PRESS_TYPE, single_press_type.value)

    async def _wall_switch_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        url = "https://wyze-sirius-service.wyzecam.com//plugin/sirius/get_iot_prop"
        keys = "iot_state,switch-power,switch-iot,single_press_type"
        return await self._get_iot_prop(url, device, keys)

    async def _wall_switch_set_iot_prop(self, device: Device, prop: WallSwitchProps, value: Any) -> None:
        url = "https://wyze-sirius-service.wyzecam.com//plugin/sirius/set_iot_prop_by_topic"
        return await self._set_iot_prop(url, device, prop.value, value)
