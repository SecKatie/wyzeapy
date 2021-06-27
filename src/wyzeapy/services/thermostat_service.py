#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from enum import Enum
from typing import Any, Dict, List

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


class TemperatureUnit(Enum):
    FAHRENHEIT = 1
    CELSIUS = 2


class Preset(Enum):
    HOME = "home"
    AWAY = "away"
    SLEEP = "sleep"


class HVACState(Enum):
    COOLING = 'cooling'
    HEATING = 'heating'
    IDLE = 'idle'


class Thermostat(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.temp_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT
        self.cool_set_point: int = 74
        self.heat_set_point: int = 64
        self.fan_mode: FanMode = FanMode.AUTO
        self.hvac_mode: HVACMode = HVACMode.AUTO
        self.preset: Preset = Preset.HOME
        self.temperature: float = 71
        self.available: bool = True
        self.humidity: int = 50
        self.hvac_state: HVACState = HVACState.IDLE


class ThermostatService(BaseService):
    async def update(self, thermostat: Thermostat) -> Thermostat:
        thermostat_props = await self._client.get_thermostat_info(thermostat)
        for prop, value in thermostat_props:
            if prop == ThermostatProps.TEMP_UNIT:
                thermostat.temp_unit = value
            elif prop == ThermostatProps.COOL_SP:
                thermostat.cool_set_point = int(value)
            elif prop == ThermostatProps.HEAT_SP:
                thermostat.heat_set_point = int(value)
            elif prop == ThermostatProps.FAN_MODE:
                thermostat.fan_mode = FanMode(value)
            elif prop == ThermostatProps.MODE_SYS:
                thermostat.hvac_mode = HVACMode(value)
            elif prop == ThermostatProps.CONFIG_SCENARIO:
                thermostat.preset = Preset(value)
            elif prop == ThermostatProps.TEMPERATURE:
                thermostat.temperature = float(value)
            elif prop == ThermostatProps.IOT_STATE:
                thermostat.available = False if not value == 'connected' else True  # pylint: disable=R1719
            elif prop == ThermostatProps.HUMIDITY:
                thermostat.humidity = int(value)
            elif prop == ThermostatProps.WORKING_STATE:
                thermostat.hvac_state = HVACState(value)

        return thermostat

    async def get_thermostats(self) -> List[Thermostat]:
        return [Thermostat(thermostat.raw_dict) for thermostat in await self._client.get_thermostats()]

    async def set_cool_point(self, thermostat: Device, temp: int):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.COOL_SP, temp)

    async def set_heat_point(self, thermostat: Device, temp: int):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.HEAT_SP, temp)

    async def set_hvac_mode(self, thermostat: Device, hvac_mode: HVACMode):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.MODE_SYS, hvac_mode.value)

    async def set_fan_mode(self, thermostat: Device, fan_mode: FanMode):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.FAN_MODE, fan_mode.value)

    async def set_preset(self, thermostat: Thermostat, preset: Preset):
        await self._client.net_client.thermostat_set_iot_prop(thermostat, ThermostatProps.CONFIG_SCENARIO, preset.value)
