"""Wyzeapy - A Python wrapper for the Wyze API."""

from .wyzeapy import Wyzeapy, TwoFactorCallback
from .devices import (
    DeviceType,
    WyzeDevice,
    WyzeCamera,
    WyzeLock,
    WyzeGateway,
    WyzeSensor,
    WyzeContactSensor,
    WyzeMotionSensor,
    WyzeLeakSensor,
    WyzeLight,
    WyzePlug,
    WyzeThermostat,
    WyzeWallSwitch,
    WyzeIrrigation,
)
from .models import (
    Token,
    WyzeUser,
    CameraEvent,
    PlugUsageRecord,
    HMSMode,
    HMSStatus,
    LockInfo,
    ThermostatMode,
    ThermostatFanMode,
    ThermostatWorkingState,
    ThermostatState,
    IrrigationZone,
)
from .services.hms import WyzeHMS
from .exceptions import (
    WyzeapyError,
    AuthenticationError,
    TwoFactorAuthRequired,
    TokenRefreshError,
    NotAuthenticatedError,
    DeviceError,
    DeviceOfflineError,
    ActionNotSupportedError,
    ActionFailedError,
    ApiError,
)

__all__ = [
    # Main client
    "Wyzeapy",
    "Token",
    "TwoFactorCallback",
    "WyzeUser",
    # Device types
    "DeviceType",
    "WyzeDevice",
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
    # Data models
    "CameraEvent",
    "PlugUsageRecord",
    "HMSMode",
    "HMSStatus",
    "LockInfo",
    "ThermostatMode",
    "ThermostatFanMode",
    "ThermostatWorkingState",
    "ThermostatState",
    "IrrigationZone",
    # Services
    "WyzeHMS",
    # Exceptions
    "WyzeapyError",
    "AuthenticationError",
    "TwoFactorAuthRequired",
    "TokenRefreshError",
    "NotAuthenticatedError",
    "DeviceError",
    "DeviceOfflineError",
    "ActionNotSupportedError",
    "ActionFailedError",
    "ApiError",
]
