#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import asyncio
import logging
import time
from threading import Thread
from typing import Any, List, Optional, Dict, Callable, Tuple

from aiohttp import ClientOSError, ContentTypeError

from wyzeapy.exceptions import UnknownApiError
from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, DeviceTypes, Event, PropertyIDs
from wyzeapy.utils import return_event_for_device, create_pid_pair

_LOGGER = logging.getLogger(__name__)


class Camera(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

        self.last_event: Optional[Event] = None
        self.last_event_ts: int = int(time.time() * 1000)
        self.on: bool = True


class CameraService(BaseService):
    _updater_thread: Optional[Thread] = None
    _subscribers: List[Tuple[Camera, Callable[[Camera], None]]] = []

    async def update(self, camera: Camera):
        # Get camera events
        response = await self._get_event_list(10)
        raw_events = response['data']['event_list']
        latest_events = [Event(raw_event) for raw_event in raw_events]

        if (event := return_event_for_device(camera, latest_events)) is not None:
            camera.last_event = event
            camera.last_event_ts = event.event_ts

        # Update camera state
        state_response: List[Tuple[PropertyIDs, Any]] = await self._get_property_list(camera)
        for property, value in state_response:
            if property is PropertyIDs.AVAILABLE:
                camera.available = value == "1"
            if property is PropertyIDs.ON:
                camera.on = value == "1"

        return camera

    async def register_for_updates(self, camera: Camera, callback: Callable[[Camera], None]):
        loop = asyncio.get_event_loop()
        if not self._updater_thread:
            self._updater_thread = Thread(target=self.update_worker, args=[loop, ], daemon=True)
            self._updater_thread.start()

        self._subscribers.append((camera, callback))

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
                    except RuntimeError as e:
                        if e == RuntimeError("Session is closed"):
                            asyncio.run_coroutine_threadsafe(self._auth_lib.gen_session(), loop).result()

    async def get_cameras(self) -> List[Camera]:
        if self._devices is None:
            self._devices = await self.get_object_list()

        cameras = [device for device in self._devices if device.type is DeviceTypes.CAMERA]

        return [Camera(camera.raw_dict) for camera in cameras]

    async def turn_on(self, camera: Camera):
        await self._run_action(camera, "power_on")

    async def turn_off(self, camera: Camera):
        await self._run_action(camera, "power_off")

    async def turn_on_notifications(self, camera: Camera):
        plist = [
            create_pid_pair(PropertyIDs.NOTIFICATION, "1")
        ]

        await self._set_property_list(camera, plist)

    async def turn_off_notifications(self, camera: Camera):
        plist = [
            create_pid_pair(PropertyIDs.NOTIFICATION, "0")
        ]

        await self._set_property_list(camera, plist)
