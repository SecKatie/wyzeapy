"""Wyze Light/Bulb device."""

from __future__ import annotations

from typing import Optional

from .base import WyzeDevice, WiFiDeviceMixin, SwitchableDeviceMixin
from ..const import PropertyID


class WyzeLight(WyzeDevice, WiFiDeviceMixin, SwitchableDeviceMixin):
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

    async def set_brightness(self, brightness: int) -> None:
        """
        Set brightness level.

        :param brightness: Brightness level (0-100)
        :type brightness: int
        :raises ActionFailedError: If setting brightness fails.
        """
        brightness = max(0, min(100, brightness))
        await self._set_property(PropertyID.BRIGHTNESS, str(brightness))

    async def set_color_temp(self, color_temp: int) -> None:
        """
        Set color temperature.

        :param color_temp: Color temperature in Kelvin (typically 2700-6500)
        :type color_temp: int
        :raises ActionFailedError: If setting color temperature fails.
        """
        await self._set_property(PropertyID.COLOR_TEMP, str(color_temp))

    async def set_color(self, color: str) -> None:
        """
        Set color (for color bulbs).

        :param color: Color as hex string (e.g., \"FF0000\" for red)
        :type color: str
        :raises ActionFailedError: If setting color fails.
        """
        await self._set_property(PropertyID.COLOR_MODE, "1")
        await self._set_property(PropertyID.COLOR, color)
