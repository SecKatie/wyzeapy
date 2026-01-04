"""Wyze Lock device."""

from __future__ import annotations

from .base import WyzeDevice


class WyzeLock(WyzeDevice):
    """Wyze Lock device."""

    @property
    def is_locked(self) -> bool:
        """Whether the lock is currently locked (switch_state 0 = locked)."""
        return self.device_params.get("switch_state", 0) == 0

    @property
    def door_open(self) -> bool:
        """Whether the door is open (for locks with door sensors)."""
        return self.device_params.get("open_close_state", 0) == 1

    async def lock(self) -> bool:
        """Lock the device."""
        client = self._ensure_client()
        return await client._lock_control(self, client._lock_action_lock)

    async def unlock(self) -> bool:
        """Unlock the device."""
        client = self._ensure_client()
        return await client._lock_control(self, client._lock_action_unlock)
