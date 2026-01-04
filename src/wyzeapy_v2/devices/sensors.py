"""Wyze sensor devices."""

from __future__ import annotations

from .base import WyzeDevice


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
