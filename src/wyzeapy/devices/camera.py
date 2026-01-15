"""Wyze Camera device."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .base import WyzeDevice, WiFiDeviceMixin, SwitchableDeviceMixin
from ..const import (
    FLOODLIGHT_MODELS,
    LAMP_SOCKET_MODELS,
    DEVICEMGMT_API_MODELS,
    PropertyID,
)
from ..wyze_api_client.models import (
    RunActionRequestActionKey,
    GetEventListBody,
    DeviceMgmtRunActionRequest,
    DeviceMgmtRunActionRequestTargetInfo,
    DeviceMgmtRunActionRequestTargetInfoType,
    DeviceMgmtRunActionRequestCapabilitiesItem,
    DeviceMgmtRunActionRequestCapabilitiesItemName,
    DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem,
)
from ..wyze_api_client.api.camera import get_event_list, device_mgmt_run_action
from ..wyze_api_client.types import Unset

if TYPE_CHECKING:
    from ..models import CameraEvent


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
    def has_floodlight(self) -> bool:
        """
        Whether this camera has a floodlight or spotlight.

        This includes:
        - Floodlight Pro (LD_CFP)
        - Battery Cam Pro with spotlight (AN_RSCW)
        - Floodlight v2 (HL_CFL2)
        - Cameras with Lamp Socket accessory
        """
        if self.product_model in FLOODLIGHT_MODELS:
            return True

        dongle_model = self.device_params.get("dongle_product_model", "")
        if dongle_model in LAMP_SOCKET_MODELS or dongle_model == "HL_CFL2":
            return True

        return False

    async def siren_on(self) -> bool:
        """Turn on camera siren."""
        return await self._run_action(RunActionRequestActionKey.SIREN_ON)

    async def siren_off(self) -> bool:
        """Turn off camera siren."""
        return await self._run_action(RunActionRequestActionKey.SIREN_OFF)

    async def floodlight_on(self) -> bool:
        """
        Turn on camera floodlight.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        return await self._set_floodlight(enabled=True)

    async def floodlight_off(self) -> bool:
        """
        Turn off camera floodlight.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        return await self._set_floodlight(enabled=False)

    async def _set_floodlight(self, enabled: bool) -> bool:
        """Set floodlight/spotlight state."""
        if self.product_model == "AN_RSCW":
            # Battery Cam Pro uses spotlight
            return await self._run_devicemgmt_action(
                DeviceMgmtRunActionRequestCapabilitiesItemName.SPOTLIGHT,
                {"on": enabled},
            )
        elif self.product_model in DEVICEMGMT_API_MODELS:
            # Floodlight Pro and other devicemgmt cameras
            return await self._run_devicemgmt_action(
                DeviceMgmtRunActionRequestCapabilitiesItemName.FLOODLIGHT,
                {"on": enabled},
            )
        else:
            # Older cameras use ACCESSORY property
            # "1" = on, "2" = off (not "0"!)
            value = "1" if enabled else "2"
            return await self._set_property(PropertyID.ACCESSORY, value)

    async def motion_detection_on(self) -> bool:
        """
        Enable motion detection on camera.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        return await self._set_motion_detection(enabled=True)

    async def motion_detection_off(self) -> bool:
        """
        Disable motion detection on camera.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        return await self._set_motion_detection(enabled=False)

    async def _set_motion_detection(self, enabled: bool) -> bool:
        """Set motion detection state."""
        value = "1" if enabled else "0"

        if self.product_model in DEVICEMGMT_API_MODELS:
            return await self._run_devicemgmt_action(
                DeviceMgmtRunActionRequestCapabilitiesItemName.IOT_DEVICE,
                {"motion-detect-recording": enabled},
            )
        else:
            # For older cameras, set both properties
            result1 = await self._set_property(PropertyID.MOTION_DETECTION, value)
            result2 = await self._set_property(
                PropertyID.MOTION_DETECTION_TOGGLE, value
            )
            return result1 and result2

    async def _run_devicemgmt_action(
        self,
        capability_name: DeviceMgmtRunActionRequestCapabilitiesItemName,
        properties: dict[str, Any],
    ) -> bool:
        """Run a device management action on a newer camera model."""
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        nonce = int(ctx.nonce())

        # Build properties list
        props_list = [
            DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem(
                prop=prop_name, value=str(prop_value)
            )
            for prop_name, prop_value in properties.items()
        ]

        body = DeviceMgmtRunActionRequest(
            capabilities=[
                DeviceMgmtRunActionRequestCapabilitiesItem(
                    name=capability_name,
                    properties=props_list,
                )
            ],
            nonce=nonce,
            target_info=DeviceMgmtRunActionRequestTargetInfo(
                id=self.mac or "",
                type_=DeviceMgmtRunActionRequestTargetInfoType.DEVICE,
            ),
        )

        devicemgmt_client = ctx.create_devicemgmt_client()
        try:
            response = await device_mgmt_run_action.asyncio(
                client=devicemgmt_client,
                body=body,
            )
            return response is not None and getattr(response, "code", None) == "1"
        finally:
            await devicemgmt_client.get_async_httpx_client().aclose()

    async def get_events(
        self,
        count: int = 20,
        begin_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> list[CameraEvent]:
        """
        Get recent events for this camera.

        :param count: Maximum number of events to retrieve (default 20).
        :type count: int
        :param begin_time: Start timestamp in milliseconds (optional).
        :type begin_time: Optional[int]
        :param end_time: End timestamp in milliseconds (optional).
        :type end_time: Optional[int]
        :returns: List of CameraEvent objects.
        :rtype: list[CameraEvent]
        """
        from ..models import CameraEvent

        ctx = self._get_context()
        await ctx.ensure_token_valid()

        client = ctx.get_main_client()

        request_kwargs: dict[str, Any] = {
            "count": count,
            "device_mac_list": [self.mac] if self.mac else [],
            **ctx.build_common_params(),
        }
        if begin_time is not None:
            request_kwargs["begin_time"] = begin_time
        if end_time is not None:
            request_kwargs["end_time"] = end_time

        response = await get_event_list.asyncio(
            client=client,
            body=GetEventListBody(**request_kwargs),
        )

        if response is None or isinstance(response.data, Unset):
            return []

        if isinstance(response.data.event_list, Unset):
            return []

        return [
            CameraEvent.from_api_response(event.to_dict())
            for event in response.data.event_list
        ]
