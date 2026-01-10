"""Wyze device base types and wrappers."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol

from ..wyze_api_client.models import (
    Device,
    RunActionRequestActionKey,
    RunActionRequest,
    RunActionRequestActionParams,
    SetPropertyRequest,
    GetDeviceInfoBody,
    GetPropertyListRequest,
)
from ..wyze_api_client.api.devices import run_action, set_property, get_device_info, get_property_list
from ..wyze_api_client.types import UNSET, Unset

if TYPE_CHECKING:
    from ..wyzeapy import Wyzeapy
    from ..context import WyzeApiContext


class _HasDeviceParams(Protocol):
    """Protocol for classes that have device_params property."""

    @property
    def device_params(self) -> Dict[str, Any]: ...


class _HasContext(Protocol):
    """Protocol for classes that have _get_context method and device attributes."""

    mac: Optional[str]
    product_model: Optional[str]

    def _get_context(self) -> WyzeApiContext: ...


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


class MainApiMixin:
    """Mixin for devices using the main API (run_action, set_property)."""

    async def _run_action(self: _HasContext, action: RunActionRequestActionKey) -> bool:
        """Execute an action on this device."""
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        client = ctx.get_main_client()

        response = await run_action.asyncio(
            client=client,
            body=RunActionRequest(
                provider_key=self.product_model or "",
                instance_id=self.mac or "",
                action_key=action,
                action_params=RunActionRequestActionParams(),
                custom_string="",
                **ctx.build_common_params(),
            ),
        )

        return response is not None and getattr(response, "code", None) == "1"

    async def _set_property(self: _HasContext, property_id: str, value: str) -> bool:
        """Set a property on this device."""
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        client = ctx.get_main_client()

        response = await set_property.asyncio(
            client=client,
            body=SetPropertyRequest(
                device_mac=self.mac or "",
                device_model=self.product_model or "",
                pid=property_id,
                pvalue=value,
                **ctx.build_common_params(),
            ),
        )

        return response is not None and getattr(response, "code", None) == "1"

    async def _get_device_info(self: _HasContext) -> Dict[str, Any]:
        """Get detailed information about this device."""
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        client = ctx.get_main_client()

        response = await get_device_info.asyncio(
            client=client,
            body=GetDeviceInfoBody(
                device_mac=self.mac or "",
                device_model=self.product_model or "",
                **ctx.build_common_params(),
            ),
        )

        if response is None or isinstance(response.data, Unset):
            return {}

        return response.data.additional_properties

    async def _get_device_properties(
        self: _HasContext, property_ids: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Get property values for this device."""
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        client = ctx.get_main_client()

        request_kwargs: Dict[str, Any] = {
            "device_mac": self.mac or "",
            "device_model": self.product_model or "",
            **ctx.build_common_params(),
        }
        if property_ids:
            request_kwargs["target_pid_list"] = property_ids

        response = await get_property_list.asyncio(
            client=client,
            body=GetPropertyListRequest(**request_kwargs),
        )

        if response is None or isinstance(response.data, Unset):
            return {}

        if isinstance(response.data.property_list, Unset):
            return {}

        result = {}
        for prop in response.data.property_list:
            if not isinstance(prop.pid, Unset) and not isinstance(prop.value, Unset):
                result[prop.pid] = prop.value
        return result


class WiFiDeviceMixin:
    """Mixin for devices with WiFi connectivity."""

    @property
    def ip_address(self: _HasDeviceParams) -> Optional[str]:
        """Device's local IP address."""
        return self.device_params.get("ip")

    @property
    def ssid(self: _HasDeviceParams) -> Optional[str]:
        """Connected WiFi network name."""
        return self.device_params.get("ssid")

    @property
    def rssi(self: _HasDeviceParams) -> Optional[int]:
        """WiFi signal strength (RSSI)."""
        rssi = self.device_params.get("rssi")
        return int(rssi) if rssi else None


class BatteryDeviceMixin:
    """Mixin for battery-powered devices."""

    @property
    def is_low_battery(self: _HasDeviceParams) -> bool:
        """Whether the device battery is low."""
        return self.device_params.get("is_low_battery", 0) == 1

    @property
    def battery_level(self: _HasDeviceParams) -> Optional[int]:
        """Battery level percentage (if available)."""
        return self.device_params.get("battery")


class SwitchableDeviceMixin(MainApiMixin):
    """Mixin for devices that can be turned on/off. Requires MainApiMixin."""

    async def turn_on(self: _HasContext) -> bool:
        """Turn on the device."""
        return await self._run_action(RunActionRequestActionKey.POWER_ON)

    async def turn_off(self: _HasContext) -> bool:
        """Turn off the device."""
        return await self._run_action(RunActionRequestActionKey.POWER_OFF)


class WyzeDevice(MainApiMixin):
    """Base wrapper for Wyze devices."""

    def __init__(self, device: Device, client: Optional[Wyzeapy] = None):
        self._device = device
        self._client: Optional[Wyzeapy] = client
        self._context: Optional[WyzeApiContext] = None
        self.nickname: Optional[str] = (
            device.nickname if device.nickname is not UNSET else None
        )
        self.mac: Optional[str] = device.mac if device.mac is not UNSET else None
        self.product_model: Optional[str] = (
            device.product_model if device.product_model is not UNSET else None
        )
        self.product_type: Optional[str] = (
            device.product_type if device.product_type is not UNSET else None
        )
        self.firmware_ver: Optional[str] = (
            device.firmware_ver if device.firmware_ver is not UNSET else None
        )
        self.hardware_ver: Optional[str] = (
            device.hardware_ver if device.hardware_ver is not UNSET else None
        )
        self.parent_device_mac: Optional[str] = (
            device.parent_device_mac if device.parent_device_mac is not UNSET else None
        )
        self.available: bool = (
            device.conn_state == 1 if device.conn_state is not UNSET else False
        )
        self.push_notifications_enabled: bool = (
            device.push_switch != 2 if device.push_switch is not UNSET else True
        )

    def _get_context(self) -> WyzeApiContext:
        """Get API context for making API calls."""
        if self._context is not None:
            return self._context
        if self._client is not None:
            self._context = self._client.get_context()
            return self._context
        raise RuntimeError(
            "Device not connected to API client. "
            "Use devices from Wyzeapy.list_devices() for control methods."
        )

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

    async def get_info(self) -> Dict[str, Any]:
        """
        Get detailed device information from the API.

        Fetches the latest device info and returns the raw data dictionary.
        This can be used to get updated device state that may not be captured
        in the initial device list.

        Returns:
            Dictionary containing detailed device information.

        Raises:
            RuntimeError: If the device is not connected to an API client.
        """
        return await self._get_device_info()

    async def get_properties(
        self, property_ids: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Get property values for this device.

        Fetches the current property values from the API. Properties represent
        device state like power status, brightness, color, etc.

        Args:
            property_ids: Optional list of specific property IDs to fetch.
                         If None, fetches all properties for the device.

        Returns:
            Dictionary mapping property ID to property value.

        Raises:
            RuntimeError: If the device is not connected to an API client.
        """
        return await self._get_device_properties(property_ids)
