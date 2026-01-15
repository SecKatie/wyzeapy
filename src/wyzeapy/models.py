"""Data models for Wyze API responses.

Each model provides typed access to common fields while preserving
the full API response via the `.raw` property for advanced use cases.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass
class Token:
    """Represents Wyze API access and refresh tokens."""

    access_token: str
    refresh_token: str
    created_at: float = field(default_factory=time.time)

    REFRESH_INTERVAL: int = 82800  # 23 hours

    @property
    def should_refresh(self) -> bool:
        """
        Check if the token needs to be refreshed.

        Tokens should be refreshed after 23 hours (82800 seconds).

        :returns: True if the token should be refreshed.
        :rtype: bool
        """
        return time.time() >= (self.created_at + self.REFRESH_INTERVAL)


@dataclass
class WyzeUser:
    """Represents a Wyze user profile."""

    notifications_enabled: bool = False

    # Identity
    user_id: str | None = None
    open_user_id: str | None = None  # Used for TUTK camera authentication

    # Profile fields
    nickname: str | None = None
    logo_url: str | None = None
    gender: str | None = None
    birthdate: str | None = None
    occupation: str | None = None

    # Body metrics (for Wyze Scale integration)
    height: float | None = None
    height_unit: str | None = None
    weight: float | None = None
    weight_unit: str | None = None
    body_type: str | None = None

    # Account info
    create_time: int | None = None  # Timestamp in milliseconds
    update_time: int | None = None  # Timestamp in milliseconds
    subscription: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    is_voip_on: bool | None = None

    # Raw data for any unmodeled fields
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> "WyzeUser":
        """
        Create WyzeUser from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: WyzeUser instance populated with response data.
        :rtype: WyzeUser
        """
        return cls(
            notifications_enabled=data.get("notification", False),
            user_id=data.get("user_id"),
            open_user_id=data.get("open_user_id"),
            nickname=data.get("nickname"),
            logo_url=data.get("logo_url"),
            gender=data.get("gender"),
            birthdate=data.get("birthdate"),
            occupation=data.get("occupation"),
            height=data.get("height"),
            height_unit=data.get("height_unit"),
            weight=data.get("weight"),
            weight_unit=data.get("weight_unit"),
            body_type=data.get("body_type"),
            create_time=data.get("create_time"),
            update_time=data.get("update_time"),
            subscription=data.get("subscription"),
            metadata=data.get("metadata"),
            is_voip_on=data.get("is_voip_on"),
            raw_data=data,
        )


@dataclass
class CameraEvent:
    """
    A camera event (motion, sound, etc.).

    :param event_id: Unique identifier for the event.
    :type event_id: str
    :param device_mac: MAC address of the device that generated the event.
    :type device_mac: str
    :param device_model: Model of the device that generated the event.
    :type device_model: str
    :param event_ts: Event timestamp in milliseconds.
    :type event_ts: int
    :param event_category: Category of the event.
    :type event_category: int
    :param event_value: Value associated with the event.
    :type event_value: str
    :param file_urls: List of URLs to event files (images/videos).
    :type file_urls: list[str]
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    event_id: str
    device_mac: str
    device_model: str
    event_ts: int  # Timestamp in milliseconds
    event_category: int
    event_value: str
    file_urls: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> CameraEvent:
        """
        Create CameraEvent from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: CameraEvent instance populated with response data.
        :rtype: CameraEvent
        """
        file_urls = []
        file_list = data.get("file_list", [])
        if file_list:
            for f in file_list:
                if isinstance(f, dict) and f.get("url"):
                    file_urls.append(f["url"])

        return cls(
            event_id=data.get("event_id", ""),
            device_mac=data.get("device_mac", ""),
            device_model=data.get("device_model", ""),
            event_ts=data.get("event_ts", 0),
            event_category=data.get("event_category", 0),
            event_value=data.get("event_value", ""),
            file_urls=file_urls,
            raw=data,
        )


@dataclass
class PlugUsageRecord:
    """
    Power usage record for a smart plug.

    :param date: Date string (format varies by API).
    :type date: str
    :param usage: Usage in watt-hours.
    :type usage: float
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    date: str  # Date string (format varies by API)
    usage: float  # Usage in watt-hours
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> PlugUsageRecord:
        """
        Create PlugUsageRecord from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: PlugUsageRecord instance populated with response data.
        :rtype: PlugUsageRecord
        """
        return cls(
            date=data.get("date", ""),
            usage=data.get("usage", 0.0),
            raw=data,
        )


class HMSMode(Enum):
    """Home Monitoring Service modes."""

    HOME = "home"
    AWAY = "away"
    DISARMED = "disarm"


@dataclass
class HMSStatus:
    """
    Home Monitoring Service status.

    :param mode: Current HMS mode.
    :type mode: HMSMode | None
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    mode: HMSMode | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> HMSStatus:
        """
        Create HMSStatus from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: HMSStatus instance populated with response data.
        :rtype: HMSStatus
        """
        mode_str = data.get("message", "")
        mode = None
        if mode_str:
            try:
                mode = HMSMode(mode_str.lower())
            except ValueError:
                pass
        return cls(mode=mode, raw=data)


@dataclass
class LockInfo:
    """
    Detailed lock information.

    :param uuid: Unique identifier for the lock.
    :type uuid: str
    :param is_online: Whether the lock is online.
    :type is_online: bool
    :param is_locked: Whether the lock is currently locked.
    :type is_locked: bool
    :param door_open: Whether the door is open.
    :type door_open: bool
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    uuid: str
    is_online: bool
    is_locked: bool
    door_open: bool
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> LockInfo:
        """
        Create LockInfo from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: LockInfo instance populated with response data.
        :rtype: LockInfo
        """
        device = data.get("device", {})
        locker_status = device.get("locker_status", {})

        return cls(
            uuid=device.get("uuid", ""),
            is_online=device.get("onoff_line", 0) == 1,
            is_locked=locker_status.get("hardlock", 0) == 1,
            door_open=device.get("door_open_status", 0) == 1,
            raw=data,
        )


class ThermostatMode(Enum):
    """Thermostat system modes."""

    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"


class ThermostatFanMode(Enum):
    """Thermostat fan modes."""

    AUTO = "auto"
    ON = "on"
    CYCLE = "cycle"


class ThermostatWorkingState(Enum):
    """Thermostat working state."""

    IDLE = "idle"
    HEATING = "heating"
    COOLING = "cooling"


@dataclass
class ThermostatState:
    """
    Current thermostat state.

    :param temperature: Current temperature.
    :type temperature: float | None
    :param humidity: Current humidity percentage.
    :type humidity: float | None
    :param cool_setpoint: Cooling setpoint.
    :type cool_setpoint: float | None
    :param heat_setpoint: Heating setpoint.
    :type heat_setpoint: float | None
    :param mode: Thermostat operating mode.
    :type mode: ThermostatMode | None
    :param fan_mode: Thermostat fan mode.
    :type fan_mode: ThermostatFanMode | None
    :param working_state: Current working state.
    :type working_state: ThermostatWorkingState | None
    :param temp_unit: Temperature unit (\"F\" or \"C\").
    :type temp_unit: str
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    temperature: float | None  # Current temperature
    humidity: float | None  # Current humidity percentage
    cool_setpoint: float | None  # Cooling setpoint
    heat_setpoint: float | None  # Heating setpoint
    mode: ThermostatMode | None
    fan_mode: ThermostatFanMode | None
    working_state: ThermostatWorkingState | None
    temp_unit: str = "F"  # "F" or "C"
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> ThermostatState:
        """
        Create ThermostatState from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: ThermostatState instance populated with response data.
        :rtype: ThermostatState
        """
        props = data.get("props", {})

        def parse_float(val: Any) -> float | None:
            if val is None or val == "":
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        def parse_enum(val: Any, enum_cls: type) -> Any | None:
            if val is None or val == "":
                return None
            try:
                return enum_cls(val.lower() if isinstance(val, str) else val)
            except ValueError:
                return None

        return cls(
            temperature=parse_float(props.get("temperature")),
            humidity=parse_float(props.get("humidity")),
            cool_setpoint=parse_float(props.get("cool_sp")),
            heat_setpoint=parse_float(props.get("heat_sp")),
            mode=parse_enum(props.get("mode_sys"), ThermostatMode),
            fan_mode=parse_enum(props.get("fan_mode"), ThermostatFanMode),
            working_state=parse_enum(
                props.get("working_state"), ThermostatWorkingState
            ),
            temp_unit=props.get("temp_unit", "F"),
            raw=data,
        )


@dataclass
class IrrigationZone:
    """
    Irrigation zone configuration.

    :param zone_id: Unique identifier for the zone.
    :type zone_id: int
    :param name: Name of the zone.
    :type name: str
    :param enabled: Whether the zone is enabled.
    :type enabled: bool
    :param duration_minutes: Default watering duration in minutes.
    :type duration_minutes: int
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    zone_id: int
    name: str
    enabled: bool
    duration_minutes: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> IrrigationZone:
        """
        Create IrrigationZone from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: IrrigationZone instance populated with response data.
        :rtype: IrrigationZone
        """
        return cls(
            zone_id=data.get("zone_id", 0),
            name=data.get("name", ""),
            enabled=data.get("enabled", False),
            duration_minutes=data.get("duration", 0),
            raw=data,
        )


@dataclass
class HomeDevice:
    """
    Device information from home favorites API.

    :param device_id: Unique device identifier.
    :type device_id: str
    :param nickname: Device nickname.
    :type nickname: str
    :param device_model: Device model string.
    :type device_model: str
    :param device_category: Device category.
    :type device_category: str
    :param is_favorite: Whether device is favorited.
    :type is_favorite: bool
    :param firmware_version: Firmware version.
    :type firmware_version: str | None
    :param hardware_version: Hardware version.
    :type hardware_version: str | None
    :param thumbnail_url: Thumbnail image URL.
    :type thumbnail_url: str | None
    :param favorite_order: Order in favorites list.
    :type favorite_order: int
    :param device_order: Order in device list.
    :type device_order: int
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    device_id: str
    nickname: str
    device_model: str
    device_category: str
    is_favorite: bool
    firmware_version: str | None = None
    hardware_version: str | None = None
    thumbnail_url: str | None = None
    favorite_order: int = 0
    device_order: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "HomeDevice":
        """
        Create HomeDevice from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: HomeDevice instance populated with response data.
        :rtype: HomeDevice
        """
        device_param = data.get("device_param", {})
        thumbnail = device_param.get("thumbnail", {})

        return cls(
            device_id=data.get("device_id", ""),
            nickname=data.get("nickname", ""),
            device_model=data.get("device_model", ""),
            device_category=data.get("device_category", ""),
            is_favorite=data.get("is_favorite", 0) == 1,
            firmware_version=device_param.get("firmware_version"),
            hardware_version=device_param.get("hardware_version"),
            thumbnail_url=thumbnail.get("url") if thumbnail.get("url") else None,
            favorite_order=data.get("favorite_order", 0),
            device_order=data.get("device_order", 0),
            raw=data,
        )


@dataclass
class HomeFavorites:
    """
    Home favorites response containing device list.

    :param home_id: Home identifier.
    :type home_id: str
    :param home_name: Home name.
    :type home_name: str
    :param devices: List of devices in the home.
    :type devices: list[HomeDevice]
    :param raw: Raw API response data.
    :type raw: dict[str, Any]
    """

    home_id: str
    home_name: str
    devices: list[HomeDevice] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "HomeFavorites":
        """
        Create HomeFavorites from API response data.

        :param data: API response data dictionary.
        :type data: dict[str, Any]
        :returns: HomeFavorites instance populated with response data.
        :rtype: HomeFavorites
        """
        device_list = data.get("device_list", [])
        devices = [HomeDevice.from_api_response(d) for d in device_list]

        return cls(
            home_id=data.get("id", ""),
            home_name=data.get("name", ""),
            devices=devices,
            raw=data,
        )

    @property
    def favorite_devices(self) -> list[HomeDevice]:
        """
        Get only devices marked as favorites.

        :returns: List of favorited devices.
        :rtype: list[HomeDevice]
        """
        return [d for d in self.devices if d.is_favorite]
