#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import asyncio
import logging
import time
from threading import Thread
from typing import Any, List, Optional, Dict, Callable, Tuple

from aiohttp import ClientOSError, ContentTypeError

from ..exceptions import UnknownApiError
from .base_service import BaseService
from .update_manager import DeviceUpdater
from ..types import Device, DeviceTypes, Event, PropertyIDs, DeviceMgmtToggleProps
from ..utils import return_event_for_device, create_pid_pair

_LOGGER = logging.getLogger(__name__)

# NOTE: Make sure to also define props in devicemgmt_create_capabilities_payload()
DEVICEMGMT_API_MODELS = ["LD_CFP", "AN_RSCW", "GW_GC1"] # Floodlight pro, battery cam pro, and OG use a diffrent api (devicemgmt)


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
        raw_events = response['data']['event_list']
        latest_events = [Event(raw_event) for raw_event in raw_events]

        if (event := return_event_for_device(camera, latest_events)) is not None:
            camera.last_event = event
            camera.last_event_ts = event.event_ts

        # Update camera state
        if (camera.product_model in DEVICEMGMT_API_MODELS): # New api
            state_response: Dict[str, Any] = await self._get_iot_prop_devicemgmt(camera)
            for propCategory in state_response['data']['capabilities']:
                if propCategory['name'] == "camera":
                    camera.motion = propCategory['properties']['motion-detect-recording']
                if propCategory['name'] == "floodlight" or propCategory['name'] == "spotlight":
                    camera.floodlight = propCategory['properties']['on']
                if propCategory['name'] == "siren":
                    camera.siren = propCategory['properties']['state']
                if propCategory['name'] == "iot-device":
                    camera.notify = propCategory['properties']['push-switch']
                    camera.on = propCategory['properties']['iot-power']
                    camera.available = propCategory['properties']['iot-state']

        else: # All other cam types (old api?)
            state_response: List[Tuple[PropertyIDs, Any]] = await self._get_property_list(camera)
            for property, value in state_response:
                if property is PropertyIDs.AVAILABLE:
                    camera.available = value == "1"
                if property is PropertyIDs.ON:
                    camera.on = value == "1"
                if property is PropertyIDs.CAMERA_SIREN:
                    camera.siren = value == "1"
                if property is PropertyIDs.ACCESSORY:
                    camera.floodlight = value == "1"
                    if camera.device_params["dongle_product_model"] == "HL_CGDC":
                        camera.garage = value == "1" # 1 = open, 2 = closed by automation or smart platform (Alexa, Google Home, Rules), 0 = closed by app
                if property is PropertyIDs.NOTIFICATION:
                    camera.notify = value == "1"
                if property is PropertyIDs.MOTION_DETECTION:
                    camera.motion = value == "1"

        return camera

    async def register_for_updates(self, camera: Camera, callback: Callable[[Camera], None]):
        loop = asyncio.get_event_loop()
        if not self._updater_thread:
            self._updater_thread = Thread(target=self.update_worker, args=[loop, ], daemon=True)
            self._updater_thread.start()

        self._subscribers.append((camera, callback))

    async def deregister_for_updates(self, camera: Camera):
        self._subscribers = [(cam, callback) for cam, callback in self._subscribers if cam.mac != camera.mac]

    def update_worker(self, loop):
        while True:
            if len(self._subscribers) < 1:
                time.sleep(0.1)
            else:
                for camera, callback in self._subscribers:
                    try:
                        callback(asyncio.run_coroutine_threadsafe(self.update(camera), loop).result())
                    except UnknownApiError as e:
                        _LOGGER.warning(f"The update method detected an UnknownApiError: {e}")
                    except ClientOSError as e:
                        _LOGGER.error(f"A network error was detected: {e}")
                    except ContentTypeError as e:
                        _LOGGER.error(f"Server returned unexpected ContentType: {e}")

    async def get_cameras(self) -> List[Camera]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        cameras = [device for device in self._devices if device.type is DeviceTypes.CAMERA]

        return [Camera(camera.raw_dict) for camera in cameras]

    async def turn_on(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._run_action_devicemgmt(camera, "power", "wakeup") # Some camera models use a diffrent api
        else: await self._run_action(camera, "power_on")

    async def turn_off(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._run_action_devicemgmt(camera, "power", "sleep") # Some camera models use a diffrent api
        else: await self._run_action(camera, "power_off")

    async def siren_on(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._run_action_devicemgmt(camera, "siren", "siren-on") # Some camera models use a diffrent api
        else: await self._run_action(camera, "siren_on")

    async def siren_off(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._run_action_devicemgmt(camera, "siren", "siren-off") # Some camera models use a diffrent api
        else: await self._run_action(camera, "siren_off")

    # Also controls lamp socket and BCP spotlight
    async def floodlight_on(self, camera: Camera):
        if (camera.product_model == "AN_RSCW"): await self._run_action_devicemgmt(camera, "spotlight", "1") # Battery cam pro integrated spotlight is controllable
        elif (camera.product_model in DEVICEMGMT_API_MODELS): await self._run_action_devicemgmt(camera, "floodlight", "1") # Some camera models use a diffrent api
        else: await self._set_property(camera, PropertyIDs.ACCESSORY.value, "1")

    # Also controls lamp socket and BCP spotlight
    async def floodlight_off(self, camera: Camera):
        if (camera.product_model == "AN_RSCW"): await self._run_action_devicemgmt(camera, "spotlight", "0") # Battery cam pro integrated spotlight is controllable
        elif (camera.product_model in DEVICEMGMT_API_MODELS): await self._run_action_devicemgmt(camera, "floodlight", "0") # Some camera models use a diffrent api
        else: await self._set_property(camera, PropertyIDs.ACCESSORY.value, "2")

    # Garage door trigger uses run action on all models
    async def garage_door_open(self, camera: Camera):
        await self._run_action(camera, "garage_door_trigger")
    
    async def garage_door_close(self, camera: Camera):
        await self._run_action(camera, "garage_door_trigger")

    async def turn_on_notifications(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._set_toggle(camera, DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value, "1")
        else: await self._set_property(camera, PropertyIDs.NOTIFICATION.value, "1")

    async def turn_off_notifications(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._set_toggle(camera, DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value, "0")
        else: await self._set_property(camera, PropertyIDs.NOTIFICATION.value, "0")

    # Both properties need to be set on newer cams, older cameras seem to only react
    # to the first property but it doesnt hurt to set both
    async def turn_on_motion_detection(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._set_toggle(camera, DeviceMgmtToggleProps.EVENT_RECORDING_TOGGLE.value, "1")
        elif (camera.product_model in ["WVOD1", "HL_WCO2"]): await self._set_property_list(camera, [create_pid_pair(PropertyIDs.WCO_MOTION_DETECTION, "1")])
        else:
            await self._set_property(camera, PropertyIDs.MOTION_DETECTION.value, "1")
            await self._set_property(camera, PropertyIDs.MOTION_DETECTION_TOGGLE.value, "1")

    async def turn_off_motion_detection(self, camera: Camera):
        if (camera.product_model in DEVICEMGMT_API_MODELS): await self._set_toggle(camera, DeviceMgmtToggleProps.EVENT_RECORDING_TOGGLE.value, "0")
        elif (camera.product_model in ["WVOD1", "HL_WCO2"]): await self._set_property_list(camera, [create_pid_pair(PropertyIDs.WCO_MOTION_DETECTION, "0")])
        else:
            await self._set_property(camera, PropertyIDs.MOTION_DETECTION.value, "0")
            await self._set_property(camera, PropertyIDs.MOTION_DETECTION_TOGGLE.value, "0")
