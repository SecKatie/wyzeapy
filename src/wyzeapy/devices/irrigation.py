"""Wyze Irrigation Controller device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import WyzeDevice
from ..const import OLIVE_APP_ID, APP_INFO
from ..exceptions import ActionFailedError, ApiRequestError
from ..wyze_api_client.models import (
    IrrigationQuickRunRequest,
    IrrigationQuickRunRequestZoneRunsItem,
    IrrigationStopRequest,
    IrrigationStopRequestAction,
)
from ..wyze_api_client.api.irrigation import (
    get_irrigation_zones,
    irrigation_quick_run,
    stop_irrigation_schedule,
)
from ..wyze_api_client.types import Unset

if TYPE_CHECKING:
    from ..models import IrrigationZone


class WyzeIrrigation(WyzeDevice):
    """Wyze Irrigation Controller device."""

    async def get_zones(self) -> list["IrrigationZone"]:
        """
        Get irrigation zones for this controller.

        Returns:
            List of IrrigationZone objects.
        """
        from ..models import IrrigationZone

        ctx = self._get_context()
        await ctx.ensure_token_valid()

        access_token = ctx.access_token
        nonce = ctx.nonce()
        device_id = self.mac or ""

        payload = {"device_id": device_id, "nonce": nonce}
        signature = ctx.olive_create_signature(payload, access_token)

        platform_client = ctx.get_platform_client()

        response = await get_irrigation_zones.asyncio(
            client=platform_client,
            device_id=device_id,
            nonce=nonce,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=ctx.phone_id,
            signature2=signature,
        )

        if response is None:
            raise ApiRequestError("get_irrigation_zones", f"device_id={device_id}")

        if isinstance(response.data, Unset):
            return []

        zones_data = getattr(response.data, "zones", [])
        if isinstance(zones_data, Unset):
            zones_data = []

        return [
            IrrigationZone.from_api_response(
                zone.to_dict() if hasattr(zone, "to_dict") else zone
            )
            for zone in zones_data
        ]

    async def run(self, zones: list[tuple[int, int]]) -> None:
        """
        Start irrigation on specified zones.

        :param zones: List of (zone_number, duration_seconds) tuples.
        :type zones: list[tuple[int, int]]
        :raises ActionFailedError: If starting irrigation fails.
        """
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        access_token = ctx.access_token
        nonce = ctx.nonce()
        device_id = self.mac or ""

        zone_runs = [
            IrrigationQuickRunRequestZoneRunsItem(zone_number=zone_num, duration=duration)
            for zone_num, duration in zones
        ]

        body = IrrigationQuickRunRequest(
            device_id=device_id,
            nonce=nonce,
            zone_runs=zone_runs,
        )

        body_dict = body.to_dict()
        signature = ctx.olive_create_signature(body_dict, access_token)

        platform_client = ctx.get_platform_client()

        response = await irrigation_quick_run.asyncio(
            client=platform_client,
            body=body,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=ctx.phone_id,
            signature2=signature,
        )

        if response is None:
            raise ActionFailedError("irrigation_run", device_id, None)
        if getattr(response, "code", None) != "1":
            raise ActionFailedError("irrigation_run", device_id, response)

    async def stop(self) -> None:
        """
        Stop all running irrigation on this controller.

        :raises ActionFailedError: If stopping irrigation fails.
        """
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        access_token = ctx.access_token
        nonce = ctx.nonce()
        device_id = self.mac or ""

        body = IrrigationStopRequest(
            device_id=device_id,
            nonce=nonce,
            action=IrrigationStopRequestAction.STOP,
        )

        body_dict = body.to_dict()
        signature = ctx.olive_create_signature(body_dict, access_token)

        platform_client = ctx.get_platform_client()

        response = await stop_irrigation_schedule.asyncio(
            client=platform_client,
            body=body,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=ctx.phone_id,
            signature2=signature,
        )

        if response is None:
            raise ActionFailedError("irrigation_stop", device_id, None)
        if getattr(response, "code", None) != "1":
            raise ActionFailedError("irrigation_stop", device_id, response)
