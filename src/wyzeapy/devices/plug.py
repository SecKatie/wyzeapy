"""Wyze Plug/Switch device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import WyzeDevice, SwitchableDeviceMixin

if TYPE_CHECKING:
    from ..models import PlugUsageRecord


class WyzePlug(WyzeDevice, SwitchableDeviceMixin):
    """Wyze Plug/Switch device."""

    @property
    def is_on(self) -> bool:
        """Whether the plug is on."""
        return self.device_params.get("switch_state", 0) == 1

    async def get_usage_history(
        self,
        start_time: int,
        end_time: int,
    ) -> list[PlugUsageRecord]:
        """
        Get power usage history for this plug.

        Args:
            start_time: Start timestamp in milliseconds.
            end_time: End timestamp in milliseconds.

        Returns:
            List of PlugUsageRecord objects with date and usage data.
        """
        client = self._ensure_client()
        return await client.get_plug_usage(self, start_time, end_time)
