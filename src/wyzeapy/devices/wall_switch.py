"""Wyze Wall Switch device."""

from __future__ import annotations

from typing import Optional

from .base import WyzeDevice, SwitchableDeviceMixin


class WyzeWallSwitch(WyzeDevice, SwitchableDeviceMixin):
    """Wyze Wall Switch device."""

    @property
    def is_on(self) -> bool:
        """Whether the switch is on."""
        return self.device_params.get("switch-power", "off") == "on"

    @property
    def iot_state(self) -> Optional[str]:
        """IoT connection state."""
        return self.device_params.get("iot_state")
