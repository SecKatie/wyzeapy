#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from enum import Enum
from typing import Any

from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, ThermostatProps


class HVACMode(Enum):
    AUTO = "auto"
    HEAT = "heat"
    COOL = "cool"


class FanMode(Enum):  # auto, on, off
    AUTO = "auto"
    ON = "on"
    OFF = "off"


class ThermostatService(BaseService):
    async def update(self, device: Any):
        pass

    async def get_thermostats(self):
        return await self._client.get_thermostats()

    async def set_cool_point(self, thermostat: Device, temp: int):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.COOL_SP, temp)

    async def set_heat_point(self, thermostat: Device, temp: int):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.HEAT_SP, temp)

    async def set_hvac_mode(self, thermostat: Device, hvac_mode: HVACMode):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.MODE_SYS, hvac_mode.value)

    async def set_fan_mode(self, thermostat: Device, fan_mode: FanMode):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.FAN_MODE, fan_mode.value)
