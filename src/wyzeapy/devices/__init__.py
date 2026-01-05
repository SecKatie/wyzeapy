"""Wyze device types and wrappers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Type

from ..wyze_api_client.models import Device
from ..wyze_api_client.types import UNSET

from .base import (
    DeviceType,
    WyzeDevice,
    WiFiDeviceMixin,
    BatteryDeviceMixin,
    SwitchableDeviceMixin,
)
from .camera import WyzeCamera
from .lock import WyzeLock
from .gateway import WyzeGateway
from .sensors import WyzeSensor, WyzeContactSensor, WyzeMotionSensor, WyzeLeakSensor
from .light import WyzeLight
from .plug import WyzePlug
from .thermostat import WyzeThermostat
from .wall_switch import WyzeWallSwitch

if TYPE_CHECKING:
    from ..wyzeapy import Wyzeapy

__all__ = [
    "DeviceType",
    "WyzeDevice",
    "WiFiDeviceMixin",
    "BatteryDeviceMixin",
    "SwitchableDeviceMixin",
    "WyzeCamera",
    "WyzeLock",
    "WyzeGateway",
    "WyzeSensor",
    "WyzeContactSensor",
    "WyzeMotionSensor",
    "WyzeLeakSensor",
    "WyzeLight",
    "WyzePlug",
    "WyzeThermostat",
    "WyzeWallSwitch",
    "create_device",
]

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
