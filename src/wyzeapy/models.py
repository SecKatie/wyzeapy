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
        """Create WyzeUser from API response data."""
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
    """A camera event (motion, sound, etc.)."""

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
    """Power usage record for a smart plug."""

    date: str  # Date string (format varies by API)
    usage: float  # Usage in watt-hours
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> PlugUsageRecord:
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
    """Home Monitoring Service status."""

    mode: HMSMode | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> HMSStatus:
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
    """Detailed lock information."""

    uuid: str
    is_online: bool
    is_locked: bool
    door_open: bool
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> LockInfo:
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
    """Current thermostat state."""

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
            working_state=parse_enum(props.get("working_state"), ThermostatWorkingState),
            temp_unit=props.get("temp_unit", "F"),
            raw=data,
        )


@dataclass
class IrrigationZone:
    """Irrigation zone configuration."""

    zone_id: int
    name: str
    enabled: bool
    duration_minutes: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> IrrigationZone:
        return cls(
            zone_id=data.get("zone_id", 0),
            name=data.get("name", ""),
            enabled=data.get("enabled", False),
            duration_minutes=data.get("duration", 0),
            raw=data,
        )


@dataclass
class HomeDevice:
    """Device information from home favorites API."""

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
    """Home favorites response containing device list."""

    home_id: str
    home_name: str
    devices: list[HomeDevice] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "HomeFavorites":
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
        """Get only devices marked as favorites."""
        return [d for d in self.devices if d.is_favorite]


