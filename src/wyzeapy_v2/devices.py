"""Wyze device types and wrappers."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from .wyze_api_client.models import Device
from .wyze_api_client.types import UNSET

if TYPE_CHECKING:
    from .wyzeapy import Wyzeapy


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
        if self._device.device_params is UNSET:
            return {}
        return self._device.device_params.additional_properties

    @property
    def raw_device(self) -> Device:
        """Access the underlying Device model."""
        return self._device

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nickname={self.nickname!r}, mac={self.mac!r}, type={self.type.value})"


class WyzeCamera(WyzeDevice):
    """Wyze Camera device."""

    @property
    def is_on(self) -> bool:
        """Whether the camera is powered on."""
        return self.device_params.get("power_switch", 0) == 1

    @property
    def motion_detection_enabled(self) -> bool:
        """Whether motion detection is enabled."""
        return self.device_params.get("motion_alarm_switch", 0) == 1

    @property
    def audio_detection_enabled(self) -> bool:
        """Whether audio detection is enabled."""
        return self.device_params.get("audio_alarm_switch", 0) == 1

    @property
    def recording_enabled(self) -> bool:
        """Whether event recording is enabled."""
        return self.device_params.get("records_event_switch", 0) == 1

    @property
    def ip_address(self) -> Optional[str]:
        """Camera's local IP address."""
        return self.device_params.get("ip")

    @property
    def ssid(self) -> Optional[str]:
        """Connected WiFi network name."""
        return self.device_params.get("ssid")

    @property
    def p2p_id(self) -> Optional[str]:
        """P2P connection ID for streaming."""
        return self.device_params.get("p2p_id")

    async def siren_on(self) -> bool:
        """Turn on camera siren."""
        client = self._ensure_client()
        return await client._run_action(self, client._action_siren_on)

    async def siren_off(self) -> bool:
        """Turn off camera siren."""
        client = self._ensure_client()
        return await client._run_action(self, client._action_siren_off)


class WyzeLock(WyzeDevice):
    """Wyze Lock device."""

    @property
    def is_locked(self) -> bool:
        """Whether the lock is currently locked (switch_state 0 = locked)."""
        return self.device_params.get("switch_state", 0) == 0

    @property
    def door_open(self) -> bool:
        """Whether the door is open (for locks with door sensors)."""
        return self.device_params.get("open_close_state", 0) == 1

    async def lock(self) -> bool:
        """Lock the device."""
        client = self._ensure_client()
        return await client._lock_control(self, client._lock_action_lock)

    async def unlock(self) -> bool:
        """Unlock the device."""
        client = self._ensure_client()
        return await client._lock_control(self, client._lock_action_unlock)


class WyzeGateway(WyzeDevice):
    """Wyze Gateway/Hub device."""

    pass


class WyzeSensor(WyzeDevice):
    """Base class for Wyze sensors (contact, motion, leak)."""

    @property
    def is_low_battery(self) -> bool:
        """Whether the sensor battery is low."""
        return self.device_params.get("is_low_battery", 0) == 1


class WyzeContactSensor(WyzeSensor):
    """Wyze Contact Sensor."""

    @property
    def is_open(self) -> bool:
        """Whether the contact sensor detects open state."""
        return self.device_params.get("open_close_state", 0) == 1


class WyzeMotionSensor(WyzeSensor):
    """Wyze Motion Sensor."""

    @property
    def motion_detected(self) -> bool:
        """Whether motion is currently detected."""
        return self.device_params.get("motion_state", 0) == 1


class WyzeLeakSensor(WyzeSensor):
    """Wyze Leak Sensor."""

    @property
    def leak_detected(self) -> bool:
        """Whether a leak is detected."""
        return self.device_params.get("leak_state", 0) == 1


class WyzeLight(WyzeDevice):
    """Wyze Light/Bulb device."""

    @property
    def is_on(self) -> bool:
        """Whether the light is on."""
        return self.device_params.get("switch_state", 0) == 1

    @property
    def brightness(self) -> Optional[int]:
        """Brightness level (0-100)."""
        return self.device_params.get("brightness")

    @property
    def color_temp(self) -> Optional[int]:
        """Color temperature in Kelvin."""
        return self.device_params.get("color_temp")

    @property
    def color(self) -> Optional[str]:
        """Color as hex string (for color bulbs)."""
        return self.device_params.get("color")

    @property
    def ip_address(self) -> Optional[str]:
        """Light's local IP address."""
        return self.device_params.get("ip")

    @property
    def ssid(self) -> Optional[str]:
        """Connected WiFi network name."""
        return self.device_params.get("ssid")

    @property
    def rssi(self) -> Optional[int]:
        """WiFi signal strength."""
        rssi = self.device_params.get("rssi")
        return int(rssi) if rssi else None

    async def set_brightness(self, brightness: int) -> bool:
        """
        Set brightness level.

        Args:
            brightness: Brightness level (0-100)

        Returns:
            True if successful
        """
        client = self._ensure_client()
        brightness = max(0, min(100, brightness))
        return await client._set_property(self, client._prop_brightness, str(brightness))

    async def set_color_temp(self, color_temp: int) -> bool:
        """
        Set color temperature.

        Args:
            color_temp: Color temperature in Kelvin (typically 2700-6500)

        Returns:
            True if successful
        """
        client = self._ensure_client()
        return await client._set_property(self, client._prop_color_temp, str(color_temp))

    async def set_color(self, color: str) -> bool:
        """
        Set color (for color bulbs).

        Args:
            color: Color as hex string (e.g., "FF0000" for red)

        Returns:
            True if successful
        """
        client = self._ensure_client()
        # Set color mode to color (1) first, then set color
        await client._set_property(self, client._prop_color_mode, "1")
        return await client._set_property(self, client._prop_color, color)


class WyzePlug(WyzeDevice):
    """Wyze Plug/Switch device."""

    @property
    def is_on(self) -> bool:
        """Whether the plug is on."""
        return self.device_params.get("switch_state", 0) == 1


class WyzeThermostat(WyzeDevice):
    """Wyze Thermostat device."""

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature."""
        return self.device_params.get("temperature")

    @property
    def humidity(self) -> Optional[int]:
        """Current humidity percentage."""
        return self.device_params.get("humidity")

    @property
    def cool_setpoint(self) -> Optional[float]:
        """Cooling setpoint temperature."""
        return self.device_params.get("cool_sp")

    @property
    def heat_setpoint(self) -> Optional[float]:
        """Heating setpoint temperature."""
        return self.device_params.get("heat_sp")

    @property
    def hvac_mode(self) -> Optional[str]:
        """HVAC mode (auto, heat, cool, off)."""
        return self.device_params.get("mode_sys")

    @property
    def fan_mode(self) -> Optional[str]:
        """Fan mode (auto, on, off)."""
        return self.device_params.get("fan_mode")

    @property
    def working_state(self) -> Optional[str]:
        """Current working state (idle, heating, cooling)."""
        return self.device_params.get("working_state")


class WyzeWallSwitch(WyzeDevice):
    """Wyze Wall Switch device."""

    @property
    def is_on(self) -> bool:
        """Whether the switch is on."""
        return self.device_params.get("switch-power", "off") == "on"

    @property
    def iot_state(self) -> Optional[str]:
        """IoT connection state."""
        return self.device_params.get("iot_state")


# Mapping from product type to device class
_DEVICE_TYPE_MAP: Dict[str, Type[WyzeDevice]] = {
    DeviceType.CAMERA.value: WyzeCamera,
    DeviceType.LOCK.value: WyzeLock,
    DeviceType.GATEWAY.value: WyzeGateway,
    DeviceType.GATEWAY_V2.value: WyzeGateway,
    DeviceType.CHIME_SENSOR.value: WyzeSensor,
    DeviceType.CONTACT_SENSOR.value: WyzeContactSensor,
    DeviceType.MOTION_SENSOR.value: WyzeMotionSensor,
    DeviceType.LEAK_SENSOR.value: WyzeLeakSensor,
    DeviceType.LIGHT.value: WyzeLight,
    DeviceType.MESH_LIGHT.value: WyzeLight,
    DeviceType.LIGHTSTRIP.value: WyzeLight,
    DeviceType.PLUG.value: WyzePlug,
    DeviceType.OUTDOOR_PLUG.value: WyzePlug,
    DeviceType.THERMOSTAT.value: WyzeThermostat,
    DeviceType.WALL_SWITCH.value: WyzeWallSwitch,
}


def create_device(device: Device, client: Optional[Wyzeapy] = None) -> WyzeDevice:
    """
    Create the appropriate WyzeDevice subclass based on product type.

    Args:
        device: The raw Device from the API
        client: Optional Wyzeapy client for device control methods

    Returns:
        A WyzeDevice subclass instance
    """
    product_type = device.product_type if device.product_type is not UNSET else None

    if product_type and product_type in _DEVICE_TYPE_MAP:
        return _DEVICE_TYPE_MAP[product_type](device, client)

    return WyzeDevice(device, client)
