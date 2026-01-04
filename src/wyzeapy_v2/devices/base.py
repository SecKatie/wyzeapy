"""Wyze device base types and wrappers."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from ..wyze_api_client.models import Device
from ..wyze_api_client.types import UNSET, Unset

if TYPE_CHECKING:
    from ..wyzeapy import Wyzeapy


class DeviceType(Enum):
    """Device type categories matching Wyze product types."""

    LIGHT = "Light"
    PLUG = "Plug"
    OUTDOOR_PLUG = "OutdoorPlug"
    MESH_LIGHT = "MeshLight"
    CAMERA = "Camera"
    CHIME_SENSOR = "ChimeSensor"
    CONTACT_SENSOR = "ContactSensor"
    MOTION_SENSOR = "MotionSensor"
    LEAK_SENSOR = "LeakSensor"
    LOCK = "Lock"
    GATEWAY = "gateway"
    GATEWAY_V2 = "GateWay"
    THERMOSTAT = "Thermostat"
    WALL_SWITCH = "WallSwitch"
    LIGHTSTRIP = "LightStrip"
    VACUUM = "JA_RO2"
    SCALE = "WyzeScale"
    BASE_STATION = "BaseStation"
    SENSE_V2_GATEWAY = "S1Gateway"
    KEYPAD = "Keypad"
    COMMON = "Common"  # Used for irrigation and other generic devices
    UNKNOWN = "Unknown"


class WyzeDevice:
    """Base wrapper for Wyze devices."""

    def __init__(self, device: Device, client: Optional[Wyzeapy] = None):
        self._device = device
        self._client: Optional[Wyzeapy] = client
        self.nickname: Optional[str] = device.nickname if device.nickname is not UNSET else None
        self.mac: Optional[str] = device.mac if device.mac is not UNSET else None
        self.product_model: Optional[str] = device.product_model if device.product_model is not UNSET else None
        self.product_type: Optional[str] = device.product_type if device.product_type is not UNSET else None
        self.firmware_ver: Optional[str] = device.firmware_ver if device.firmware_ver is not UNSET else None
        self.hardware_ver: Optional[str] = device.hardware_ver if device.hardware_ver is not UNSET else None
        self.parent_device_mac: Optional[str] = (
            device.parent_device_mac if device.parent_device_mac is not UNSET else None
        )
        self.available: bool = device.conn_state == 1 if device.conn_state is not UNSET else False
        self.push_notifications_enabled: bool = device.push_switch != 2 if device.push_switch is not UNSET else True

    def _ensure_client(self) -> Wyzeapy:
        """Ensure we have a client for API calls."""
        if self._client is None:
            raise RuntimeError(
                "Device not connected to API client. "
                "Use devices from Wyzeapy.list_devices() for control methods."
            )
        return self._client

    async def turn_on(self) -> bool:
        """Turn on the device."""
        client = self._ensure_client()
        return await client._run_action(self, client._action_power_on)

    async def turn_off(self) -> bool:
        """Turn off the device."""
        client = self._ensure_client()
        return await client._run_action(self, client._action_power_off)

    @property
    def type(self) -> DeviceType:
        """Get the device type enum."""
        if self.product_type is None:
            return DeviceType.UNKNOWN
        try:
            return DeviceType(self.product_type)
        except ValueError:
            return DeviceType.UNKNOWN

    @property
    def device_params(self) -> Dict[str, Any]:
        """Get device parameters as a dictionary."""
        params = self._device.device_params
        if isinstance(params, Unset):
            return {}
        return params.additional_properties

    @property
    def raw_device(self) -> Device:
        """Access the underlying Device model."""
        return self._device

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nickname={self.nickname!r}, mac={self.mac!r}, type={self.type.value})"
