"""Wyze Home Monitoring Service (HMS) API."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..models import HMSMode, HMSStatus
from ..utils import olive_create_signature
from ..const import OLIVE_APP_ID, APP_INFO
from ..exceptions import ActionFailedError
from ..wyze_api_client.api.hms import get_hms_status, set_hms_mode
from ..wyze_api_client.models import HMSProfileActiveRequestItem
from ..wyze_api_client.models.hms_profile_active_request_item_state import (
    HMSProfileActiveRequestItemState,
)
from ..wyze_api_client.models.hms_profile_active_request_item_active import (
    HMSProfileActiveRequestItemActive,
)
from ..wyze_api_client.types import Unset

if TYPE_CHECKING:
    from ..wyzeapy import Wyzeapy


class WyzeHMS:
    """
    Wyze Home Monitoring Service API.

    Access this via ``wyze.hms`` property on the main client.

    Example::

        async with Wyzeapy(email, password, key_id, api_key) as wyze:
            # Get HMS status
            status = await wyze.hms.get_status("your-hms-id")
            print(f"Current mode: {status.mode}")

            # Set HMS mode
            await wyze.hms.set_mode("your-hms-id", HMSMode.AWAY)
    """

    def __init__(self, client: "Wyzeapy"):
        self._client = client

    async def get_status(self, hms_id: str) -> HMSStatus:
        """
        Get current HMS status.

        :param hms_id: The HMS system ID.
        :type hms_id: str
        :returns: HMSStatus object with current mode and raw API response.
        :rtype: HMSStatus
        """
        await self._client._ensure_token_valid()

        access_token = self._client._get_token().access_token
        nonce = str(int(time.time() * 1000))
        payload = {"hms_id": hms_id, "nonce": nonce}
        signature = olive_create_signature(payload, access_token)

        platform_client = self._client._get_platform_client()

        response = await get_hms_status.asyncio(
            client=platform_client,
            hms_id=hms_id,
            nonce=nonce,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=self._client._phone_id,
            signature2=signature,
        )

        if response is None:
            return HMSStatus(mode=None, raw={})

        raw_data = response.to_dict() if hasattr(response, "to_dict") else {}

        message = None
        if not isinstance(response.message, Unset) and response.message:
            message = response.message

        return HMSStatus.from_api_response({"message": message, **raw_data})

    async def set_mode(self, hms_id: str, mode: HMSMode) -> None:
        """
        Set HMS mode.

        :param hms_id: The HMS system ID.
        :type hms_id: str
        :param mode: The mode to set (HOME, AWAY, or DISARMED).
        :type mode: HMSMode
        :raises ActionFailedError: If setting the mode fails.
        """
        await self._client._ensure_token_valid()

        access_token = self._client._get_token().access_token

        # Build the request body
        if mode == HMSMode.DISARMED:
            # Disarmed means setting active=0 (disabled)
            body = [
                HMSProfileActiveRequestItem(
                    state=HMSProfileActiveRequestItemState.HOME,
                    active=HMSProfileActiveRequestItemActive.VALUE_0,
                ),
            ]
        else:
            # Home or Away mode with active=1 (enabled)
            state = (
                HMSProfileActiveRequestItemState.HOME
                if mode == HMSMode.HOME
                else HMSProfileActiveRequestItemState.AWAY
            )
            body = [
                HMSProfileActiveRequestItem(
                    state=state,
                    active=HMSProfileActiveRequestItemActive.VALUE_1,
                ),
            ]

        # Create signature for the body - we know these are set since we just created them
        state_val = body[0].state
        active_val = body[0].active
        # Type narrowing: hasattr check ensures we only access .value on enum types
        state_str = state_val.value if hasattr(state_val, "value") else str(state_val)
        active_int = active_val.value if hasattr(active_val, "value") else 1
        body_dict = {
            "state": state_str,
            "active": active_int,
        }
        signature = olive_create_signature(body_dict, access_token)

        platform_client = self._client._get_platform_client()

        response = await set_hms_mode.asyncio(
            client=platform_client,
            body=body,
            hms_id=hms_id,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=self._client._phone_id,
            signature2=signature,
        )

        if response is None:
            raise ActionFailedError("set_hms_mode", hms_id, None)
        if getattr(response, "code", None) != "1":
            raise ActionFailedError("set_hms_mode", hms_id, response)

    async def disarm(self, hms_id: str) -> None:
        """
        Disarm HMS (convenience method).

        :param hms_id: The HMS system ID.
        :type hms_id: str
        :raises ActionFailedError: If disarming fails.
        """
        await self.set_mode(hms_id, HMSMode.DISARMED)
