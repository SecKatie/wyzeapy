import logging
from dataclasses import dataclass, field
from enum import Enum
import json
from time import time
from typing import Any, Dict, List

from .base_service import BaseService
from ..types import Device, IrrigationProps, DeviceTypes

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IrrigationRun:
    """A currently active sprinkler zone run."""

    zone_number: int
    zone_name: str | None
    start_ts: int | None
    end_ts: int | None
    schedule_name: str | None
    schedule_type: str | None


@dataclass(frozen=True, slots=True)
class IrrigationControllerInfo:
    """Configuration and diagnostic properties for a sprinkler controller."""

    schedules_enabled: bool | None
    wiring: Any = None
    sensor: Any = None
    notification_enabled: Any = None
    notification_watering_begins: Any = None
    notification_watering_ends: Any = None
    notification_watering_is_skipped: Any = None
    skip_low_temp: Any = None
    skip_wind: Any = None
    skip_rain: Any = None
    skip_saturation: Any = None
    raw_dict: Dict[str, Any] = field(default_factory=dict, repr=False)


def _timestamp(value: Any) -> int | None:
    """Return a valid Unix timestamp from an API value."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _integer(value: Any) -> int | None:
    """Return a valid integer from an API value."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _boolean(value: Any) -> bool | None:
    """Return a normalized boolean from an API value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        normalized = value.casefold()
        if normalized in {"1", "true", "on", "enabled"}:
            return True
        if normalized in {"0", "false", "off", "disabled"}:
            return False
    return None


def _find_property(value: Any, name: str) -> Any:
    """Find a named property in nested Wyze response formats."""
    if isinstance(value, dict):
        if name in value:
            return value[name]

        property_name = value.get("key", value.get("name"))
        if property_name == name and "value" in value:
            return value["value"]

        for nested_value in value.values():
            result = _find_property(nested_value, name)
            if result is not None:
                return result
        return None

    if isinstance(value, list):
        for nested_value in value:
            result = _find_property(nested_value, name)
            if result is not None:
                return result
        return None

    if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
        try:
            return _find_property(json.loads(value), name)
        except json.JSONDecodeError:
            return None

    return None


def _parse_current_run(
    response: Dict[Any, Any], now_timestamp: int | None = None
) -> IrrigationRun | None:
    """Parse the active zone whose time interval contains the current time."""
    now_timestamp = int(time()) if now_timestamp is None else now_timestamp
    schedules = response.get("data", {}).get("schedules", [])

    for schedule in schedules:
        if schedule.get("schedule_state") != "running":
            continue

        zone_runs = schedule.get("zone_runs") or []
        if not zone_runs:
            return None

        current_run = next(
            (
                zone_run
                for zone_run in zone_runs
                if (start := _timestamp(zone_run.get("start_ts"))) is not None
                and start <= now_timestamp
                and (
                    (end := _timestamp(zone_run.get("end_ts"))) is None
                    or now_timestamp < end
                )
            ),
            None,
        )
        if current_run is None and len(zone_runs) == 1:
            only_run = zone_runs[0]
            if (
                _timestamp(only_run.get("start_ts")) is None
                and _timestamp(only_run.get("end_ts")) is None
            ):
                current_run = only_run
        if current_run is None:
            return None

        zone_number = _integer(current_run.get("zone_number"))
        if zone_number is None:
            return None

        return IrrigationRun(
            zone_number=zone_number,
            zone_name=current_run.get("zone_name"),
            start_ts=_timestamp(current_run.get("start_ts")),
            end_ts=_timestamp(current_run.get("end_ts")),
            schedule_name=schedule.get("schedule_name"),
            schedule_type=current_run.get(
                "schedule_type", schedule.get("schedule_type")
            ),
        )

    return None


def _parse_controller_info(response: Dict[Any, Any]) -> IrrigationControllerInfo:
    """Parse controller properties while retaining the raw API data."""
    data = response.get("data", {})
    return IrrigationControllerInfo(
        schedules_enabled=_boolean(_find_property(data, "enable_schedules")),
        wiring=_find_property(data, "wiring"),
        sensor=_find_property(data, "sensor"),
        notification_enabled=_find_property(data, "notification_enable"),
        notification_watering_begins=_find_property(
            data, "notification_watering_begins"
        ),
        notification_watering_ends=_find_property(data, "notification_watering_ends"),
        notification_watering_is_skipped=_find_property(
            data, "notification_watering_is_skipped"
        ),
        skip_low_temp=_find_property(data, "skip_low_temp"),
        skip_wind=_find_property(data, "skip_wind"),
        skip_rain=_find_property(data, "skip_rain"),
        skip_saturation=_find_property(data, "skip_saturation"),
        raw_dict=data if isinstance(data, dict) else {"value": data},
    )


class CropType(Enum):
    COOL_SEASON_GRASS = "cool_season_grass"
    WARM_SEASON_GRASS = "warm_season_grass"
    SHRUBS = "shrubs"
    TREES = "trees"
    ANNUALS = "annuals"
    PERENNIALS = "perennials"
    XERISCAPE = "xeriscape"
    GARDEN = "garden"


class ExposureType(Enum):
    LOTS_OF_SUN = "lots_of_sun"
    SOME_SHADE = "some_shade"


class NozzleType(Enum):
    FIXED_SPRAY_HEAD = "fixed_spray_head"
    ROTOR_HEAD = "rotor_head"
    ROTARY_NOZZLE = "rotary_nozzle"
    MISTER = "mister"
    BUBBLER = "bubbler"
    EMITTER = "emitter"
    DRIP_LINE = "drip_line"


class SlopeType(Enum):
    FLAT = "flat"
    SLIGHT = "slight"
    MODERATE = "moderate"
    STEEP = "steep"


class SoilType(Enum):
    CLAY_LOAM = "clay_loam"
    CLAY = "clay"
    SILTY_CLAY = "silty_clay"
    LOAM = "loam"
    SANDY_LOAM = "sandy_loam"
    LOAMY_SAND = "loamy_sand"
    SAND = "sand"


class Zone:
    """Represents a single irrigation zone."""

    def __init__(self, dictionary: Dict[Any, Any]):
        self.zone_number: int = dictionary.get("zone_number", 1)
        self.name: str = dictionary.get("name", "Zone 1")
        self.enabled: bool = dictionary.get("enabled", True)
        self.zone_id: str = dictionary.get("zone_id", "zone_id")
        self.smart_duration: int = dictionary.get("smart_duration", 600)

        # this quickrun duration is used only for running a zone manually
        # the wyze api has no such value, but takes a duration as part of the api call
        # the default value grabs the wyze smart_duration but all further updates
        # are managed through the home assistant state
        self.quickrun_duration: int = dictionary.get("smart_duration", 600)


class Irrigation(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        # the below comes from the get_iot_prop call
        self.RSSI: int = 0
        self.IP: str = "192.168.1.100"
        self.sn: str = "SN123456789"
        self.available: bool = False
        self.ssid: str = "ssid"
        # the below comes from the device_info call
        self.zones: List[Zone] = []


class IrrigationService(BaseService):
    async def update(self, irrigation: Irrigation) -> Irrigation:
        """Update the irrigation device with latest data from Wyze API."""
        # Get IoT properties
        properties = (await self.get_iot_prop(irrigation))["data"]["props"]

        # Update device properties
        irrigation.RSSI = properties.get("RSSI", -65)
        irrigation.IP = properties.get("IP", "192.168.1.100")
        irrigation.sn = properties.get("sn", "SN123456789")
        irrigation.ssid = properties.get("ssid", "ssid")
        irrigation.available = (
            properties.get(IrrigationProps.IOT_STATE.value) == "connected"
        )

        # Get zones
        zones = (await self.get_zone_by_device(irrigation))["data"]["zones"]

        # Update zones
        irrigation.zones = []
        for zone in zones:
            irrigation.zones.append(Zone(zone))

        return irrigation

    async def update_device_props(self, irrigation: Irrigation) -> Irrigation:
        """Update the irrigation device with latest data from Wyze API."""
        # Get IoT properties
        properties = (await self.get_iot_prop(irrigation))["data"]["props"]

        # Update device properties
        irrigation.RSSI = properties.get("RSSI")
        irrigation.IP = properties.get("IP")
        irrigation.sn = properties.get("sn")
        irrigation.ssid = properties.get("ssid")
        irrigation.available = (
            properties.get(IrrigationProps.IOT_STATE.value) == "connected"
        )

        return irrigation

    async def get_irrigations(self) -> List[Irrigation]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        irrigations = [
            device
            for device in self._devices
            if device.type == DeviceTypes.IRRIGATION
            and "BS_WK1" in device.product_model
        ]

        return [Irrigation(irrigation.raw_dict) for irrigation in irrigations]

    async def start_zone(
        self, irrigation: Device, zone_number: int, quickrun_duration: int
    ) -> Dict[Any, Any]:
        """Start a zone with the specified duration.

        Args:
            irrigation: The irrigation device
            zone_number: The zone number to start
            quickrun_duration: Duration in seconds to run the zone

        Returns:
            Dict containing the API response
        """
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/quickrun"
        return await self._start_zone(url, irrigation, zone_number, quickrun_duration)

    async def stop_running_schedule(self, device: Device) -> Dict[Any, Any]:
        """Stop any currently running irrigation schedule.

        Args:
            device: The irrigation device

        Returns:
            Dict containing the API response
        """
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/runningschedule"
        action = "STOP"
        return await self._stop_running_schedule(url, device, action)

    async def set_zone_quickrun_duration(
        self, irrigation: Irrigation, zone_number: int, duration: int
    ) -> Irrigation:
        """Set the quickrun duration for a specific zone.

        Args:
            irrigation: The irrigation device
            zone_number: The zone number to configure
            duration: Duration in seconds for quickrun
        """
        for zone in irrigation.zones:
            if zone.zone_number == zone_number:
                zone.quickrun_duration = duration
                break

        return irrigation

    # Private implementation methods
    async def get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        """Get IoT properties for a device."""
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/get_iot_prop"
        keys = (
            "zone_state,iot_state,iot_state_update_time,app_version,RSSI,"
            "wifi_mac,sn,device_model,ssid,IP"
        )
        return await self._get_iot_prop(url, device, keys)

    async def get_device_info(self, device: Device) -> Dict[Any, Any]:
        """Get the raw device-info response from the Wyze API."""
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/device_info"
        keys = (
            "wiring,sensor,enable_schedules,notification_enable,notification_watering_begins,"
            "notification_watering_ends,notification_watering_is_skipped,skip_low_temp,skip_wind,"
            "skip_rain,skip_saturation"
        )
        return await self._irrigation_device_info(url, device, keys)

    async def get_controller_info(self, device: Device) -> IrrigationControllerInfo:
        """Get normalized sprinkler controller configuration."""
        return _parse_controller_info(await self.get_device_info(device))

    async def get_zone_by_device(self, device: Device) -> List[Dict[Any, Any]]:
        """Get zones for a device."""
        url = "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/zone"
        return await self._get_zone_by_device(url, device)

    async def get_schedule_runs(self, device: Device) -> Dict[Any, Any]:
        """Get schedule runs for an irrigation device.

        Args:
            device: The irrigation device

        Returns:
            Dict containing running status and zone information if running
        """
        url = (
            "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/schedule_runs"
        )
        response = await self._get_schedule_runs(url, device, limit=2)
        if "data" not in response or "schedules" not in response["data"]:
            _LOGGER.warning(
                "No schedule data found in response for device %s", device.mac
            )
            return {"running": False}

        for schedule in response["data"]["schedules"]:
            if schedule.get("schedule_state") != "running":
                continue
            zone_runs = schedule.get("zone_runs") or []
            if not zone_runs:
                return {"running": True}
            zone_run = zone_runs[0]
            return {
                "running": True,
                "zone_number": zone_run.get("zone_number"),
                "zone_name": zone_run.get("zone_name"),
            }

        return {"running": False}

    async def get_current_run(
        self, device: Device, *, now_timestamp: int | None = None
    ) -> IrrigationRun | None:
        """Get the zone that is currently watering, including timer metadata."""
        url = (
            "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/schedule_runs"
        )
        response = await self._get_schedule_runs(url, device, limit=2)
        return _parse_current_run(response, now_timestamp)
