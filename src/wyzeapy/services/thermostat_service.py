#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
from enum import Enum
from typing import Any, Dict, List

from .base_service import BaseService
from ..types import Device, ThermostatProps, DeviceTypes

_LOGGER = logging.getLogger(__name__)


class HVACMode(Enum):
    AUTO = "auto"
    HEAT = "heat"
    COOL = "cool"
    OFF = "off"


class FanMode(Enum):  # auto, on
    AUTO = "auto"
    ON = "on"


class TemperatureUnit(Enum):
    FAHRENHEIT = "F"
    CELSIUS = "C"


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
        properties = (await self._thermostat_get_iot_prop(thermostat))['data']['props']

        device_props = []
        for property in properties:
            try:
                prop = ThermostatProps(property)
                device_props.append((prop, properties[property]))
            except ValueError as e:
                _LOGGER.debug(f"{e} with value {properties[property]}")

        thermostat_props = device_props
        for prop, value in thermostat_props:
            if prop == ThermostatProps.TEMP_UNIT:
                thermostat.temp_unit = TemperatureUnit(value)
            elif prop == ThermostatProps.COOL_SP:
                thermostat.cool_set_point = int(value)
            elif prop == ThermostatProps.HEAT_SP:
                thermostat.heat_set_point = int(value)
            elif prop == ThermostatProps.FAN_MODE:
                thermostat.fan_mode = FanMode(value)
            elif prop == ThermostatProps.MODE_SYS:
                thermostat.hvac_mode = HVACMode(value)
            elif prop == ThermostatProps.CURRENT_SCENARIO:
                thermostat.preset = Preset(value)
            elif prop == ThermostatProps.TEMPERATURE:
                thermostat.temperature = float(value)
            elif prop == ThermostatProps.IOT_STATE:
                thermostat.available = value == 'connected'
            elif prop == ThermostatProps.HUMIDITY:
                thermostat.humidity = int(value)
            elif prop == ThermostatProps.WORKING_STATE:
                thermostat.hvac_state = HVACState(value)

        return thermostat

    async def get_thermostats(self) -> List[Thermostat]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        thermostats = [device for device in self._devices if device.type is DeviceTypes.THERMOSTAT]

        return [Thermostat(thermostat.raw_dict) for thermostat in thermostats]

    async def set_cool_point(self, thermostat: Device, temp: int):
        await self._thermostat_set_iot_prop(thermostat, ThermostatProps.COOL_SP, temp)

    async def set_heat_point(self, thermostat: Device, temp: int):
        await self._thermostat_set_iot_prop(thermostat, ThermostatProps.HEAT_SP, temp)

    async def set_hvac_mode(self, thermostat: Device, hvac_mode: HVACMode):
        await self._thermostat_set_iot_prop(thermostat, ThermostatProps.MODE_SYS, hvac_mode.value)

    async def set_fan_mode(self, thermostat: Device, fan_mode: FanMode):
        await self._thermostat_set_iot_prop(thermostat, ThermostatProps.FAN_MODE, fan_mode.value)

    async def set_preset(self, thermostat: Thermostat, preset: Preset):
        await self._thermostat_set_iot_prop(thermostat, ThermostatProps.CURRENT_SCENARIO, preset.value)

    async def _thermostat_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/get_iot_prop"
        keys = 'trigger_off_val,emheat,temperature,humidity,time2temp_val,protect_time,mode_sys,heat_sp,cool_sp,' \
                'current_scenario,config_scenario,temp_unit,fan_mode,iot_state,w_city_id,w_lat,w_lon,working_state,' \
                'dev_hold,dev_holdtime,asw_hold,app_version,setup_state,wiring_logic_id,save_comfort_balance,' \
                'kid_lock,calibrate_humidity,calibrate_temperature,fancirc_time,query_schedule'
        return await self._get_iot_prop(url, device, keys)

    async def _thermostat_set_iot_prop(self, device: Device, prop: ThermostatProps, value: Any) -> None:
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic"
        return await self._set_iot_prop(url, device, prop.value, value)
