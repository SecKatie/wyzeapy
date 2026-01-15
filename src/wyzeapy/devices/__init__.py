"""Wyze device types and wrappers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..wyze_api_client.models import Device
from ..utils import or_none

_logger = logging.getLogger(__name__)

from .base import (
    DeviceType,
    WyzeDevice,
    WiFiDeviceMixin,
    BatteryDeviceMixin,
    SwitchableDeviceMixin,
)
from .camera import WyzeCamera
from .gateway import WyzeGateway
from .irrigation import WyzeIrrigation
from .light import WyzeLight
from .lock import WyzeLock
from .plug import WyzePlug
from .sensors import WyzeSensor, WyzeContactSensor, WyzeMotionSensor, WyzeLeakSensor
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
    "WyzeIrrigation",
    "create_device",
]

# Mapping from product type to device class
_DEVICE_TYPE_MAP: dict[str, type[WyzeDevice]] = {
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
    DeviceType.COMMON.value: WyzeIrrigation,  # Irrigation controllers use "Common" type
}


def create_device(device: Device, client: "Wyzeapy | None" = None) -> WyzeDevice:
    """
    Create the appropriate WyzeDevice subclass based on product type.

    Args:
        device: The raw Device from the API
        client: Optional Wyzeapy client for device control methods

    Returns:
        A WyzeDevice subclass instance
    """
    product_type = or_none(device.product_type)

    if product_type and product_type in _DEVICE_TYPE_MAP:
        return _DEVICE_TYPE_MAP[product_type](device, client)

    if product_type:
        _logger.warning(
            (
                "Unknown device type '%s' for device '%s' (mac=%s). "
                "Falling back to base WyzeDevice. Consider reporting this device type."
            ),
            product_type,
            or_none(device.nickname) or "unknown",
            or_none(device.mac) or "unknown",
        )

    return WyzeDevice(device, client)
