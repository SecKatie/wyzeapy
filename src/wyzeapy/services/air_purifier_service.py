import logging
import time
from enum import Enum
from typing import Any, Dict, List

from .base_service import BaseService
from ..types import AirPurifierProps, Device, DeviceTypes, PropertyIDs

_LOGGER = logging.getLogger(__name__)

AIR_PURIFIER_MODELS = {"CO_AP1"}


class AirPurifierFanMode(Enum):
    AUTO = "auto"
    SLEEP = "sleep"
    MIN = "min"
    MID = "mid"
    MAX = "max"
    TURBO = "turbo"


class AirPurifier(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.on: bool = False
        self.available: bool = False
        self.fan_mode: str = AirPurifierFanMode.AUTO.value
        self.aqi: int | None = None
        self.max_hourly_aqi: int | None = None
        self.max_hourly_aqi_start_time: int | None = None
        self.max_hourly_aqi_end_time: int | None = None
        self.app_version: str | None = None
        self.sn: str | None = None
        self.wifi_mac: str | None = None


class AirPurifierService(BaseService):
    async def update(self, air_purifier: AirPurifier) -> AirPurifier:
        """Update the air purifier with latest data from Wyze API."""
        device_info = await self._get_property_list(air_purifier)
        for property_id, value in device_info:
            if property_id == PropertyIDs.ON:
                air_purifier.on = value == "1"
            elif property_id == PropertyIDs.AVAILABLE:
                air_purifier.available = value == "1"

        properties = (await self._air_purifier_get_iot_prop(air_purifier))["data"][
            "props"
        ]

        device_props = []
        for prop_key, prop_value in properties.items():
            try:
                prop = AirPurifierProps(prop_key)
                device_props.append((prop, prop_value))
            except ValueError as err:
                _LOGGER.debug(f"{err} with value {prop_value}")

        for prop, value in device_props:
            if prop == AirPurifierProps.IOT_STATE:
                air_purifier.available = value == "connected"
            elif prop == AirPurifierProps.FAN_MODE:
                air_purifier.fan_mode = value
            elif prop == AirPurifierProps.APP_VERSION:
                air_purifier.app_version = value
            elif prop == AirPurifierProps.SN:
                air_purifier.sn = value
            elif prop == AirPurifierProps.WIFI_MAC:
                air_purifier.wifi_mac = value

        return air_purifier

    async def update_air_quality(self, air_purifier: AirPurifier) -> AirPurifier:
        response = await self._air_purifier_get_air_prop(air_purifier)
        settings = response.get("data", {}).get("settings", {})
        aqi = settings.get(AirPurifierProps.AQI.value)
        air_purifier.aqi = self._parse_int(aqi)

        await self._air_purifier_update_max_hourly_aqi(air_purifier)

        return air_purifier

    async def get_air_purifiers(self) -> List[AirPurifier]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        air_purifiers = [
            device
            for device in self._devices
            if device.type is DeviceTypes.COMMON
            and device.product_model in AIR_PURIFIER_MODELS
        ]

        return [AirPurifier(air_purifier.raw_dict) for air_purifier in air_purifiers]

    async def turn_on(self, air_purifier: AirPurifier):
        await self._set_property(air_purifier, PropertyIDs.ON.value, "1")

    async def turn_off(self, air_purifier: AirPurifier):
        await self._set_property(air_purifier, PropertyIDs.ON.value, "0")

    async def set_fan_mode(
        self, air_purifier: AirPurifier, fan_mode: AirPurifierFanMode | str
    ) -> None:
        if isinstance(fan_mode, AirPurifierFanMode):
            fan_mode = fan_mode.value
        await self._air_purifier_set_iot_prop(
            air_purifier, AirPurifierProps.FAN_MODE, fan_mode
        )

    async def _air_purifier_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/get_iot_prop"
        keys = "iot_state,fan_mode,app_version,sn,wifi_mac"
        return await self._get_iot_prop(url, device, keys)

    async def _air_purifier_get_air_prop(self, device: Device) -> Dict[Any, Any]:
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/get_air_prop"
        return await self._get_air_prop(url, device, AirPurifierProps.AQI.value)

    async def _air_purifier_update_max_hourly_aqi(
        self, air_purifier: AirPurifier
    ) -> None:
        begin_time, last_time = self._air_quality_hour()
        response = await self._air_purifier_query_air_history(
            air_purifier, begin_time=begin_time, last_time=last_time
        )

        air_purifier.max_hourly_aqi_start_time = begin_time
        air_purifier.max_hourly_aqi_end_time = last_time
        air_purifier.max_hourly_aqi = self._get_max_hourly_aqi(
            response.get("data") or []
        )

    @staticmethod
    def _air_quality_hour() -> tuple[int, int]:
        last_time = int(time.time())
        begin_time = last_time - (last_time % 3600)
        return begin_time, last_time

    @classmethod
    def _get_max_hourly_aqi(cls, history: List[Dict[Any, Any]]) -> int | None:
        for sample in reversed(history):
            max_aqi = cls._parse_int(sample.get("max_aqi"))
            avg_aqi = cls._parse_int(sample.get("avg"))
            if max_aqi is not None and (
                max_aqi > 0 or (avg_aqi is not None and avg_aqi >= 0)
            ):
                return max_aqi
        return None

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    async def _air_purifier_query_air_history(
        self, device: Device, begin_time: int, last_time: int
    ) -> Dict[Any, Any]:
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/query_air_history"
        return await self._query_air_history(url, device, begin_time, last_time)

    async def _air_purifier_set_iot_prop(
        self, device: Device, prop: AirPurifierProps, value: Any
    ) -> None:
        url = (
            "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic"
        )
        return await self._set_iot_prop(url, device, prop.value, value)
