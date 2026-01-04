"""Wyze Thermostat device."""

from __future__ import annotations

from typing import Optional

from .base import WyzeDevice


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
