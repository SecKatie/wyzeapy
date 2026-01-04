"""Wyze Camera device."""

from __future__ import annotations

from typing import Optional

from .base import WyzeDevice, WiFiDeviceMixin, SwitchableDeviceMixin


class WyzeCamera(WyzeDevice, WiFiDeviceMixin, SwitchableDeviceMixin):
    """Wyze Camera device."""

    @property
    def is_on(self) -> bool:
        """Whether the camera is powered on."""
        return self.device_params.get("power_switch", 0) == 1

    @property
    def motion_detection_enabled(self) -> bool:
        """Whether motion detection is enabled."""
        return self.device_params.get("motion_alarm_switch", 0) == 1

    @property
    def audio_detection_enabled(self) -> bool:
        """Whether audio detection is enabled."""
        return self.device_params.get("audio_alarm_switch", 0) == 1

    @property
    def recording_enabled(self) -> bool:
        """Whether event recording is enabled."""
        return self.device_params.get("records_event_switch", 0) == 1

    @property
    def p2p_id(self) -> Optional[str]:
        """P2P connection ID for streaming."""
        return self.device_params.get("p2p_id")

    async def siren_on(self) -> bool:
        """Turn on camera siren."""
        client = self._ensure_client()
        return await client.run_action(self, client._action_siren_on)

    async def siren_off(self) -> bool:
        """Turn off camera siren."""
        client = self._ensure_client()
        return await client.run_action(self, client._action_siren_off)
