"""Wyzeapy - A Python wrapper for the Wyze API."""

from .wyzeapy import Wyzeapy, Token, TwoFactorCallback
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
)
from .exceptions import (
    WyzeapyError,
    AuthenticationError,
    TwoFactorAuthRequired,
    TokenRefreshError,
    NotAuthenticatedError,
    DeviceError,
    DeviceOfflineError,
    ActionNotSupportedError,
    ApiError,
)

__all__ = [
    # Main client
    "Wyzeapy",
    "Token",
    "TwoFactorCallback",
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
    # Exceptions
    "WyzeapyError",
    "AuthenticationError",
    "TwoFactorAuthRequired",
    "TokenRefreshError",
    "NotAuthenticatedError",
    "DeviceError",
    "DeviceOfflineError",
    "ActionNotSupportedError",
    "ApiError",
]