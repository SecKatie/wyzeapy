"""Wyze Light/Bulb device."""

from __future__ import annotations

from typing import Optional

from .base import WyzeDevice


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
