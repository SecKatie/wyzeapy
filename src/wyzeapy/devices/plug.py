"""Wyze Plug/Switch device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import WyzeDevice, SwitchableDeviceMixin
from ..wyze_api_client.models import PlugUsageRequest
from ..wyze_api_client.api.switch import get_plug_usage_history
from ..wyze_api_client.types import Unset

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
    ) -> list["PlugUsageRecord"]:
        """
        Get power usage history for this plug.

        :param start_time: Start timestamp in milliseconds.
        :type start_time: int
        :param end_time: End timestamp in milliseconds.
        :type end_time: int
        :returns: List of PlugUsageRecord objects with date and usage data.
        :rtype: list[PlugUsageRecord]
        """
        from ..models import PlugUsageRecord

        ctx = self._get_context()
        await ctx.ensure_token_valid()

        client = ctx.get_main_client()

        response = await get_plug_usage_history.asyncio(
            client=client,
            body=PlugUsageRequest(
                device_mac=self.mac or "",
                date_begin=start_time,
                date_end=end_time,
                **ctx.build_common_params(),
            ),
        )

        if response is None or isinstance(response.data, Unset):
            return []

        if isinstance(response.data.usage_record_list, Unset):
            return []

        return [
            PlugUsageRecord.from_api_response(record.to_dict())
            for record in response.data.usage_record_list
        ]
