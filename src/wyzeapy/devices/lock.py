"""Wyze Lock device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import WyzeDevice
from ..wyze_api_client.models import LockControlRequestAction

if TYPE_CHECKING:
    from ..models import LockInfo


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
        return await client._lock_control(self, LockControlRequestAction.REMOTELOCK)

    async def unlock(self) -> bool:
        """Unlock the device."""
        client = self._ensure_client()
        return await client._lock_control(self, LockControlRequestAction.REMOTEUNLOCK)

    async def get_info(self, with_keypad: bool = False) -> "LockInfo":
        """
        Get detailed lock information from the API.

        Args:
            with_keypad: Whether to include keypad information.

        Returns:
            LockInfo object with lock status, door state, and online status.
        """
        client = self._ensure_client()
        return await client.get_lock_info(self, with_keypad=with_keypad)
