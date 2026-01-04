from enum import Enum
from typing import Any, Optional

from ..wyze_api_client.models import Device


class DeviceType(Enum):
    CAMERA = "Camera"
    LOCK = "Lock"
    GATEWAY = "gateway"
    CHIME_SENSOR = "ChimeSensor"
    LIGHT = "Light"

class WyzeDevice:
    def __init__(self, device: Device):
        self.device = device
        self.nickname = device.nickname
        self.mac = device.mac
        self.product_model = device.product_model
        self.firmware_ver = device.firmware_ver
        self.hardware_ver = device.hardware_ver
        self.available = device.conn_state != 0
        self.push_notifications_enabled = device.push_switch != 2
        self.device_params = device.device_params
        self.additional_properties = device.additional_properties

    def __repr__(self) -> str:
        return (
            f"WyzeDevice(\n"
            f"  nickname={self.nickname},\n"
            f"  mac={self.mac},\n"
            f"  product_model={self.product_model},\n"
            f"  firmware_ver={self.firmware_ver},\n"
            f"  hardware_ver={self.hardware_ver},\n"
            f"  available={self.available},\n"
            f"  push_notifications_enabled={self.push_notifications_enabled},\n"
            f"  device_params={self.device_params},\n"
            f"  additional_properties={self.additional_properties})"
            f")"
        )

class WyzeCamera(WyzeDevice):
    def __init__(self, device: Device):
        super().__init__(device)
        self.type = DeviceType.CAMERA

class WyzeLock(WyzeDevice):
    def __init__(self, device: Device):
        super().__init__(device)
        self.type = DeviceType.LOCK

class WyzeGateway(WyzeDevice):
    def __init__(self, device: Device):
        super().__init__(device)
        self.type = DeviceType.GATEWAY

class WyzeChimeSensor(WyzeDevice):
    def __init__(self, device: Device):
        super().__init__(device)
        self.type = DeviceType.CHIME_SENSOR

class WyzeLight(WyzeDevice):
    def __init__(self, device: Device):
        super().__init__(device)
        self.type = DeviceType.LIGHT
        self.is_on: Optional[bool] = None
        if device.device_params is not None and type(device.device_params.additional_properties) == dict:
            self.is_on = True if device.device_params.additional_properties.get("switch_state", None) == 1 else False
            
    
    def __repr__(self) -> str:
        return f"WyzeLight(is_on={self.is_on})"
    

def create_device(device: Device) -> WyzeDevice:
    type_map = {
        DeviceType.CAMERA: WyzeCamera,
        DeviceType.LOCK: WyzeLock,
        DeviceType.GATEWAY: WyzeGateway,
        DeviceType.CHIME_SENSOR: WyzeChimeSensor,
        DeviceType.LIGHT: WyzeLight,
    }

    return type_map[DeviceType(device.product_type)](device)