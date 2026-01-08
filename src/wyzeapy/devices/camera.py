"""Wyze Camera device."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import WyzeDevice, WiFiDeviceMixin, SwitchableDeviceMixin
from ..const import FLOODLIGHT_MODELS, LAMP_SOCKET_MODELS
from ..wyze_api_client.models import RunActionRequestActionKey

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
    def p2p_id(self) -> Optional[str]:
        """P2P connection ID for streaming."""
        return self.device_params.get("p2p_id")

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
        # Check if this is a known floodlight model
        if self.product_model in FLOODLIGHT_MODELS:
            return True

        # Check for lamp socket accessory via dongle_product_model
        dongle_model = self.device_params.get("dongle_product_model", "")
        if dongle_model in LAMP_SOCKET_MODELS or dongle_model == "HL_CFL2":
            return True

        return False

    async def siren_on(self) -> bool:
        """Turn on camera siren."""
        client = self._ensure_client()
        return await client.run_action(self, RunActionRequestActionKey.SIREN_ON)

    async def siren_off(self) -> bool:
        """Turn off camera siren."""
        client = self._ensure_client()
        return await client.run_action(self, RunActionRequestActionKey.SIREN_OFF)

    async def floodlight_on(self) -> bool:
        """
        Turn on camera floodlight.

        Returns:
            True if successful, False otherwise.

        Raises:
            ActionNotSupportedError: If the camera doesn't have a floodlight.
        """
        client = self._ensure_client()
        return await client.set_camera_floodlight(self, enabled=True)

    async def floodlight_off(self) -> bool:
        """
        Turn off camera floodlight.

        Returns:
            True if successful, False otherwise.

        Raises:
            ActionNotSupportedError: If the camera doesn't have a floodlight.
        """
        client = self._ensure_client()
        return await client.set_camera_floodlight(self, enabled=False)

    async def motion_detection_on(self) -> bool:
        """
        Enable motion detection on the camera.

        Returns:
            True if successful, False otherwise.
        """
        client = self._ensure_client()
        return await client.set_camera_motion_detection(self, enabled=True)

    async def motion_detection_off(self) -> bool:
        """
        Disable motion detection on the camera.

        Returns:
            True if successful, False otherwise.
        """
        client = self._ensure_client()
        return await client.set_camera_motion_detection(self, enabled=False)

    async def get_events(
        self,
        count: int = 20,
        begin_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> list[CameraEvent]:
        """
        Get recent events for this camera.

        Args:
            count: Maximum number of events to retrieve (default 20).
            begin_time: Start timestamp in milliseconds (optional).
            end_time: End timestamp in milliseconds (optional).

        Returns:
            List of CameraEvent objects.
        """
        client = self._ensure_client()
        return await client.get_camera_events(
            self, count=count, begin_time=begin_time, end_time=end_time
        )
