"""Wyze Thermostat device."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import WyzeDevice

if TYPE_CHECKING:
    from ..models import ThermostatState


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

    async def get_state(self) -> "ThermostatState":
        """
        Get current thermostat state from the API.

        Returns:
            ThermostatState object with current temperature, setpoints, and mode.
        """
        client = self._ensure_client()
        return await client.get_thermostat_state(self)

    async def set_cool_setpoint(self, temperature: int) -> bool:
        """
        Set the cooling setpoint temperature.

        Args:
            temperature: The target cooling temperature.

        Returns:
            True if successful, False otherwise.
        """
        client = self._ensure_client()
        return await client.set_thermostat_properties(self, cool_setpoint=temperature)

    async def set_heat_setpoint(self, temperature: int) -> bool:
        """
        Set the heating setpoint temperature.

        Args:
            temperature: The target heating temperature.

        Returns:
            True if successful, False otherwise.
        """
        client = self._ensure_client()
        return await client.set_thermostat_properties(self, heat_setpoint=temperature)

    async def set_hvac_mode(self, mode: str) -> bool:
        """
        Set the HVAC mode.

        Args:
            mode: The mode ('off', 'heat', 'cool', 'auto').

        Returns:
            True if successful, False otherwise.
        """
        client = self._ensure_client()
        return await client.set_thermostat_properties(self, hvac_mode=mode)

    async def set_fan_mode(self, mode: str) -> bool:
        """
        Set the fan mode.

        Args:
            mode: The mode ('auto', 'on', 'cycle').

        Returns:
            True if successful, False otherwise.
        """
        client = self._ensure_client()
        return await client.set_thermostat_properties(self, fan_mode=mode)
