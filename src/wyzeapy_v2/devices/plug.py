"""Wyze Plug/Switch device."""

from __future__ import annotations

from .base import WyzeDevice, SwitchableDeviceMixin


class WyzePlug(WyzeDevice, SwitchableDeviceMixin):
    """Wyze Plug/Switch device."""

    @property
    def is_on(self) -> bool:
        """Whether the plug is on."""
        return self.device_params.get("switch_state", 0) == 1
