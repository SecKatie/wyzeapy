#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import json
import logging
from enum import Enum
from typing import Any, Dict, List

from wyzeapy.const import OLIVE_APP_ID, APP_INFO, PHONE_ID
from wyzeapy.crypto import olive_create_signature
from wyzeapy.exceptions import ActionNotSupported
from wyzeapy.payload_factory import olive_create_get_payload, olive_create_post_payload
from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, ThermostatProps, DeviceTypes
from wyzeapy.utils import check_for_errors_thermostat

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
            elif prop == ThermostatProps.CONFIG_SCENARIO:
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
            self._devices = await self._get_devices()

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
        await self._thermostat_set_iot_prop(thermostat, ThermostatProps.CONFIG_SCENARIO, preset.value)

    async def _thermostat_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        payload = olive_create_get_payload(device.mac)
        signature = olive_create_signature(payload, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        url = 'https://wyze-earth-service.wyzecam.com/plugin/earth/get_iot_prop'

        response_json = await self._auth_lib.get(url, headers=headers, params=payload)

        check_for_errors_thermostat(response_json)

        return response_json

    async def _thermostat_set_iot_prop(self, device: Device, prop: ThermostatProps, value: Any) -> None:
        await self._auth_lib.refresh_if_should()

        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic"
        payload = olive_create_post_payload(device.mac, device.product_model, prop, value)
        signature = olive_create_signature(json.dumps(payload, separators=(',', ':')),
                                           self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        payload_str = json.dumps(payload, separators=(',', ':'))

        response_json = await self._auth_lib.post(url, headers=headers, data=payload_str)

        check_for_errors_thermostat(response_json)

















