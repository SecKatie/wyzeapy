"""Wyze Lock device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import WyzeDevice
from ..const import FORD_APP_KEY
from ..exceptions import ActionFailedError, ApiRequestError
from ..wyze_api_client.models import LockControlRequest, LockControlRequestAction
from ..wyze_api_client.api.lock import lock_control, get_lock_info

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

    async def lock(self) -> None:
        """
        Lock the device.

        :raises ActionFailedError: If the action fails.
        """
        await self._lock_control(LockControlRequestAction.REMOTELOCK)

    async def unlock(self) -> None:
        """
        Unlock the device.

        :raises ActionFailedError: If the action fails.
        """
        await self._lock_control(LockControlRequestAction.REMOTEUNLOCK)

    async def _lock_control(self, action: LockControlRequestAction) -> None:
        """Control the lock."""
        ctx = self._get_context()
        lock_client = await ctx.lock_client()

        timestamp = ctx.nonce()
        device_uuid = self.mac or ""
        access_token = await ctx.get_access_token()

        payload = {
            "access_token": access_token,
            "action": action.value,
            "key": FORD_APP_KEY,
            "timestamp": timestamp,
            "uuid": device_uuid,
        }

        signature = ctx.ford_create_signature(
            "/openapi/lock/v1/control", "POST", payload
        )

        response = await lock_control.asyncio(
            client=lock_client,
            body=LockControlRequest(
                sign=signature,
                uuid=device_uuid,
                action=action,
                access_token=access_token,
                key=FORD_APP_KEY,
                timestamp=timestamp,
            ),
        )

        if response is None:
            raise ActionFailedError(action.value, device_uuid, None)
        if getattr(response, "code", 1) != 0:
            raise ActionFailedError(action.value, device_uuid, response)

    async def get_lock_info(self, with_keypad: bool = False) -> "LockInfo":
        """
        Get detailed lock information as a typed LockInfo object.

        :param with_keypad: Whether to include keypad information.
        :type with_keypad: bool
        :returns: LockInfo object with lock status, door state, and online status.
        :rtype: LockInfo
        """
        from ..models import LockInfo

        ctx = self._get_context()
        lock_client = await ctx.lock_client()

        timestamp = ctx.nonce()
        device_uuid = self.mac or ""
        access_token = await ctx.get_access_token()

        payload = {
            "access_token": access_token,
            "key": FORD_APP_KEY,
            "timestamp": timestamp,
            "uuid": device_uuid,
        }
        if with_keypad:
            payload["with_keypad"] = "1"

        signature = ctx.ford_create_signature(
            "/openapi/lock/v1/info", "GET", payload
        )

        response = await get_lock_info.asyncio(
            client=lock_client,
            uuid=device_uuid,
            access_token=access_token,
            key=FORD_APP_KEY,
            timestamp=timestamp,
            sign=signature,
        )

        if response is None:
            raise ApiRequestError("get_lock_info", f"uuid={device_uuid}")

        raw_data = response.to_dict() if hasattr(response, "to_dict") else {}
        return LockInfo.from_api_response(raw_data)
