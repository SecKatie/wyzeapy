"""Wyze Camera device."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
from ..exceptions import ActionFailedError, ApiRequestError

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

    async def siren_on(self) -> None:
        """
        Turn on camera siren.

        :raises ActionFailedError: If the action fails.
        """
        await self._run_action(RunActionRequestActionKey.SIREN_ON)

    async def siren_off(self) -> None:
        """
        Turn off camera siren.

        :raises ActionFailedError: If the action fails.
        """
        await self._run_action(RunActionRequestActionKey.SIREN_OFF)

    async def floodlight_on(self) -> None:
        """
        Turn on camera floodlight.

        :raises ActionFailedError: If the action fails.
        """
        await self._set_floodlight(enabled=True)

    async def floodlight_off(self) -> None:
        """
        Turn off camera floodlight.

        :raises ActionFailedError: If the action fails.
        """
        await self._set_floodlight(enabled=False)

    async def _set_floodlight(self, enabled: bool) -> None:
        """Set floodlight/spotlight state."""
        if self.product_model == "AN_RSCW":
            # Battery Cam Pro uses spotlight
            await self._run_devicemgmt_action(
                DeviceMgmtRunActionRequestCapabilitiesItemName.SPOTLIGHT,
                {"on": enabled},
            )
        elif self.product_model in DEVICEMGMT_API_MODELS:
            # Floodlight Pro and other devicemgmt cameras
            await self._run_devicemgmt_action(
                DeviceMgmtRunActionRequestCapabilitiesItemName.FLOODLIGHT,
                {"on": enabled},
            )
        else:
            # Older cameras use ACCESSORY property
            # "1" = on, "2" = off (not "0"!)
            value = "1" if enabled else "2"
            await self._set_property(PropertyID.ACCESSORY, value)

    async def motion_detection_on(self) -> None:
        """
        Enable motion detection on camera.

        :raises ActionFailedError: If the action fails.
        """
        await self._set_motion_detection(enabled=True)

    async def motion_detection_off(self) -> None:
        """
        Disable motion detection on camera.

        :raises ActionFailedError: If the action fails.
        """
        await self._set_motion_detection(enabled=False)

    async def _set_motion_detection(self, enabled: bool) -> None:
        """Set motion detection state."""
        value = "1" if enabled else "0"

        if self.product_model in DEVICEMGMT_API_MODELS:
            await self._run_devicemgmt_action(
                DeviceMgmtRunActionRequestCapabilitiesItemName.IOT_DEVICE,
                {"motion-detect-recording": enabled},
            )
        else:
            # For older cameras, set both properties
            await self._set_property(PropertyID.MOTION_DETECTION, value)
            await self._set_property(PropertyID.MOTION_DETECTION_TOGGLE, value)

    async def _run_devicemgmt_action(
        self,
        capability_name: DeviceMgmtRunActionRequestCapabilitiesItemName,
        properties: dict[str, Any],
    ) -> None:
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

        devicemgmt_client = ctx.get_devicemgmt_client()

        response = await device_mgmt_run_action.asyncio(
            client=devicemgmt_client,
            body=body,
        )

        if response is None:
            raise ActionFailedError(capability_name.value, self.mac or "", None)
        if getattr(response, "code", None) != "1":
            raise ActionFailedError(capability_name.value, self.mac or "", response)

    async def get_events(
        self,
        count: int = 20,
        begin_time: int | None = None,
        end_time: int | None = None,
    ) -> list[CameraEvent]:
        """
        Get recent events for this camera.

        :param count: Maximum number of events to retrieve (default 20).
        :param begin_time: Start timestamp in milliseconds (optional).
        :param end_time: End timestamp in milliseconds (optional).
        :returns: List of CameraEvent objects.
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

        if response is None:
            raise ApiRequestError("get_camera_events", f"device_mac={self.mac}")

        if isinstance(response.data, Unset):
            return []

        if isinstance(response.data.event_list, Unset):
            return []

        return [
            CameraEvent.from_api_response(event.to_dict())
            for event in response.data.event_list
        ]
