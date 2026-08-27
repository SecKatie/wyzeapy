#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import asyncio
import base64
import json
import logging
import random
import time
from threading import Thread
from typing import Any, List, Optional, Dict, Callable, Tuple

from aiohttp import ClientOSError, ContentTypeError

from ..crypto import xxtea_decrypt_b64
from ..exceptions import UnknownApiError
from .base_service import BaseService
from ..types import (
    Device,
    DeviceTypes,
    Event,
    PropertyIDs,
    DeviceMgmtToggleProps,
    ResponseCodes,
)
from ..utils import return_event_for_device, create_pid_pair

_LOGGER = logging.getLogger(__name__)

# NOTE: Make sure to also define props in devicemgmt_create_capabilities_payload()
DEVICEMGMT_API_MODELS = [
    "LD_CFP",
    "AN_RSCW",
    "GW_GC1",
    "HL_PAN4",  # Wyze Cam Pan v4
    "ME_WCO3",  # Wyze Solar Cam Pan
]  # Floodlight pro, battery cam pro, OG, Pan v4, and Solar Cam Pan use a diffrent api (devicemgmt)

# Cameras that livestream via Agora RTC (Wyze provider name "lake") instead of
# AWS Kinesis WebRTC signaling. These never join the Kinesis signaling channel
# that the "webrtc" provider hands out, so get_stream_info must request the
# "lake" provider and issue Agora credentials via wcsa/create-connection.
LAKE_API_MODELS = [
    "ME_WCO3",  # Wyze Solar Cam Pan
]


class Camera(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.last_event: Optional[Event] = None
        self.last_event_ts: int = int(time.time() * 1000)
        self.on: bool = True
        self.siren: bool = False
        self.floodlight: bool = False
        self.garage: bool = False


class CameraService(BaseService):
    _updater_thread: Optional[Thread] = None
    _subscribers: List[Tuple[Camera, Callable[[Camera], None]]] = []

    async def update(self, camera: Camera):
        # Get updated device_params
        async with BaseService._update_lock:
            camera.device_params = await self.get_updated_params(camera.mac)

        # Get camera events
        response = await self._get_event_list(10)
        raw_events = response["data"]["event_list"]
        latest_events = [Event(raw_event) for raw_event in raw_events]

        if (event := return_event_for_device(camera, latest_events)) is not None:
            camera.last_event = event
            camera.last_event_ts = event.event_ts

        # Update camera state
        if camera.product_model in DEVICEMGMT_API_MODELS:  # New api
            state_response: Dict[str, Any] = await self._get_iot_prop_devicemgmt(camera)
            for propCategory in state_response["data"]["capabilities"]:
                if propCategory["name"] == "camera":
                    camera.motion = propCategory["properties"][
                        "motion-detect-recording"
                    ]
                if (
                    propCategory["name"] == "floodlight"
                    or propCategory["name"] == "spotlight"
                ):
                    camera.floodlight = propCategory["properties"]["on"]
                if propCategory["name"] == "siren":
                    camera.siren = propCategory["properties"]["state"]
                if propCategory["name"] == "iot-device":
                    camera.notify = propCategory["properties"]["push-switch"]
                    camera.on = propCategory["properties"]["iot-power"]
                    camera.available = propCategory["properties"]["iot-state"]

        else:  # All other cam types (old api?)
            state_response: List[
                Tuple[PropertyIDs, Any]
            ] = await self._get_property_list(camera)
            for property, value in state_response:
                if property is PropertyIDs.AVAILABLE:
                    camera.available = value == "1"
                if property is PropertyIDs.ON:
                    camera.on = value == "1"
                if property is PropertyIDs.CAMERA_SIREN:
                    camera.siren = value == "1"
                if property is PropertyIDs.ACCESSORY:
                    # Bulb Cam (HL_BC): '1' = ON, '2' = OFF
                    # Other cameras with accessories: same logic
                    camera.floodlight = value == "1"
                    if camera.device_params.get("dongle_product_model") == "HL_CGDC":
                        camera.garage = (
                            value == "1"
                        )  # 1 = open, 2 = closed by automation or smart platform (Alexa, Google Home, Rules), 0 = closed by app
                if property is PropertyIDs.NOTIFICATION:
                    camera.notify = value == "1"
                if property is PropertyIDs.MOTION_DETECTION:
                    camera.motion = value == "1"

        return camera

    async def register_for_updates(
        self, camera: Camera, callback: Callable[[Camera], None]
    ):
        loop = asyncio.get_event_loop()
        if not self._updater_thread:
            self._updater_thread = Thread(
                target=self.update_worker,
                args=[
                    loop,
                ],
                daemon=True,
            )
            self._updater_thread.start()

        self._subscribers.append((camera, callback))

    async def deregister_for_updates(self, camera: Camera):
        self._subscribers = [
            (cam, callback)
            for cam, callback in self._subscribers
            if cam.mac != camera.mac
        ]

    def update_worker(self, loop):
        while True:
            if len(self._subscribers) < 1:
                time.sleep(0.1)
            else:
                for camera, callback in self._subscribers:
                    try:
                        callback(
                            asyncio.run_coroutine_threadsafe(
                                self.update(camera), loop
                            ).result()
                        )
                    except UnknownApiError as e:
                        _LOGGER.warning(
                            f"The update method detected an UnknownApiError: {e}"
                        )
                    except ClientOSError as e:
                        _LOGGER.error(f"A network error was detected: {e}")
                    except ContentTypeError as e:
                        _LOGGER.error(f"Server returned unexpected ContentType: {e}")

    async def get_cameras(self) -> List[Camera]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        cameras = [
            device for device in self._devices if device.type is DeviceTypes.CAMERA
        ]

        return [Camera(camera.raw_dict) for camera in cameras]

    async def turn_on(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._run_action_devicemgmt(
                camera, "power", "wakeup"
            )  # Some camera models use a diffrent api
        else:
            await self._run_action(camera, "power_on")

    async def turn_off(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._run_action_devicemgmt(
                camera, "power", "sleep"
            )  # Some camera models use a diffrent api
        else:
            await self._run_action(camera, "power_off")

    async def siren_on(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._run_action_devicemgmt(
                camera, "siren", "siren-on"
            )  # Some camera models use a diffrent api
        else:
            await self._run_action(camera, "siren_on")

    async def siren_off(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._run_action_devicemgmt(
                camera, "siren", "siren-off"
            )  # Some camera models use a diffrent api
        else:
            await self._run_action(camera, "siren_off")

    # Also controls lamp socket, BCP spotlight, and Bulb Cam light
    async def floodlight_on(self, camera: Camera):
        if camera.product_model in ("AN_RSCW", "HL_PAN4", "ME_WCO3"):
            await self._run_action_devicemgmt(
                camera, "spotlight", "1"
            )  # Battery cam pro, Pan v4, and Solar Cam Pan have an integrated spotlight
        elif camera.product_model in DEVICEMGMT_API_MODELS:
            await self._run_action_devicemgmt(
                camera, "floodlight", "1"
            )  # Some camera models use a diffrent api
        elif camera.product_model == "HL_BC":
            # Bulb Cam uses run_action with floodlight_on action
            await self._run_action(camera, "floodlight_on")
        else:
            await self._set_property(camera, PropertyIDs.ACCESSORY.value, "1")

    # Also controls lamp socket, BCP spotlight, and Bulb Cam light
    async def floodlight_off(self, camera: Camera):
        if camera.product_model in ("AN_RSCW", "HL_PAN4", "ME_WCO3"):
            await self._run_action_devicemgmt(
                camera, "spotlight", "0"
            )  # Battery cam pro, Pan v4, and Solar Cam Pan have an integrated spotlight
        elif camera.product_model in DEVICEMGMT_API_MODELS:
            await self._run_action_devicemgmt(
                camera, "floodlight", "0"
            )  # Some camera models use a diffrent api
        elif camera.product_model == "HL_BC":
            # Bulb Cam uses run_action with floodlight_off action
            await self._run_action(camera, "floodlight_off")
        else:
            await self._set_property(camera, PropertyIDs.ACCESSORY.value, "2")

    # Garage door trigger uses run action on all models
    async def garage_door_open(self, camera: Camera):
        await self._run_action(camera, "garage_door_trigger")

    async def garage_door_close(self, camera: Camera):
        await self._run_action(camera, "garage_door_trigger")

    async def turn_on_notifications(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._set_toggle(
                camera, DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value, "1"
            )
        else:
            await self._set_property(camera, PropertyIDs.NOTIFICATION.value, "1")

    async def turn_off_notifications(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._set_toggle(
                camera, DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value, "0"
            )
        else:
            await self._set_property(camera, PropertyIDs.NOTIFICATION.value, "0")

    # Both properties need to be set on newer cams, older cameras seem to only react
    # to the first property but it doesnt hurt to set both
    async def turn_on_motion_detection(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._set_toggle(
                camera, DeviceMgmtToggleProps.EVENT_RECORDING_TOGGLE.value, "1"
            )
        elif camera.product_model in ["WVOD1", "HL_WCO2"]:
            await self._set_property_list(
                camera, [create_pid_pair(PropertyIDs.WCO_MOTION_DETECTION, "1")]
            )
        else:
            await self._set_property(camera, PropertyIDs.MOTION_DETECTION.value, "1")
            await self._set_property(
                camera, PropertyIDs.MOTION_DETECTION_TOGGLE.value, "1"
            )

    async def turn_off_motion_detection(self, camera: Camera):
        if camera.product_model in DEVICEMGMT_API_MODELS:
            await self._set_toggle(
                camera, DeviceMgmtToggleProps.EVENT_RECORDING_TOGGLE.value, "0"
            )
        elif camera.product_model in ["WVOD1", "HL_WCO2"]:
            await self._set_property_list(
                camera, [create_pid_pair(PropertyIDs.WCO_MOTION_DETECTION, "0")]
            )
        else:
            await self._set_property(camera, PropertyIDs.MOTION_DETECTION.value, "0")
            await self._set_property(
                camera, PropertyIDs.MOTION_DETECTION_TOGGLE.value, "0"
            )

    def _user_id_from_token(self) -> str:
        """Extract the Wyze account user_id claim from the JWT access token."""
        claims_segment = self._auth_lib.token.access_token.split(".")[1]
        claims_segment += "=" * (-len(claims_segment) % 4)
        claims = json.loads(base64.urlsafe_b64decode(claims_segment))
        return claims["user_id"]

    async def get_stream_info(self, camera: Camera):
        if camera.product_model in LAKE_API_MODELS:
            return await self._get_lake_stream_info(camera)
        data = await self._get_camera_stream(camera)
        if data.get("code") == ResponseCodes.DEVICE_OFFLINE.value:
            raise UnknownApiError(
                "Camera is offline according to get_stream_info response: " + str(data)
            )
        if "data" not in data or len(data["data"]) != 1:
            raise UnknownApiError(
                "Unexpected response from get_stream_info: " + str(data)
            )

        data = data["data"][0]
        if "property" not in data:
            raise UnknownApiError(
                "Unexpected response from get_stream_info: " + str(data)
            )
        if data["property"]["iot-device::iot-state"] != 1:
            raise UnknownApiError(
                "Camera is offline according to get_stream_info response: " + str(data)
            )
        if data["property"]["iot-device::iot-power"] != 1:
            raise UnknownApiError(
                "Camera is off according to get_stream_info response: " + str(data)
            )
        return data["params"]

    async def _get_lake_stream_info(self, camera: Camera):
        """Stream connection info for cameras that livestream via Agora RTC.

        Mirrors the Wyze web portal's flow: get-streams with provider
        "lake" (returns the Agora channel and encryption key/salt), wake
        the camera so it joins the channel, then create-connection for
        the Agora app_id/rtc_token/uid. Returns a params dict with all of
        those merged, plus provider="lake" so callers can tell it apart
        from the Kinesis "webrtc" config.
        """
        rtc_client_uid = random.randint(10000, 999999)

        data = await self._get_camera_stream(camera, provider="lake")
        if data.get("code") == ResponseCodes.DEVICE_OFFLINE.value:
            raise UnknownApiError(
                "Camera is offline according to get_stream_info response: " + str(data)
            )
        if "data" not in data or len(data["data"]) != 1:
            raise UnknownApiError(
                "Unexpected response from get_stream_info: " + str(data)
            )
        data = data["data"][0]
        if data.get("property", {}).get("iot-device::iot-state") != 1:
            raise UnknownApiError(
                "Camera is offline according to get_stream_info response: " + str(data)
            )

        await self._wakeup_device(camera, self._user_id_from_token(), rtc_client_uid)
        connection = await self._create_rtc_connection(camera, rtc_client_uid)

        params = dict(data["params"])
        params.update(connection["data"])
        params["provider"] = "lake"

        # The Agora stream key/salt are XXTEA-encrypted with the account
        # access token. Decrypt so callers get values usable directly with
        # Agora's setEncryptionConfig (key as a string, salt as 32 base64
        # bytes to decode into a Uint8Array).
        token = self._auth_lib.token.access_token
        if params.get("encryption_key"):
            params["encryption_key"] = xxtea_decrypt_b64(
                params["encryption_key"], token
            )
        if params.get("encryption_salt"):
            params["encryption_salt"] = xxtea_decrypt_b64(
                params["encryption_salt"], token
            )
        return params
