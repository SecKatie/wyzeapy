#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import asyncio
import logging
import time
from threading import Thread
from typing import List, Callable

from aiohttp import ClientOSError, ContentTypeError

from ..exceptions import UnknownApiError, _AuthenticationInProgress
from .base_service import BaseService
from ..types import Device, PropertyIDs, DeviceTypes

_LOGGER = logging.getLogger(__name__)

# device_params key holding the detected state, per sensor type
_STATE_KEYS = {
    DeviceTypes.MOTION_SENSOR: "motion_state",
    DeviceTypes.CONTACT_SENSOR: "open_close_state",
    DeviceTypes.LEAK_SENSOR: "ws_detect_state",
}


class Sensor(Device):
    detected: bool = False


class SensorService(BaseService):
    def __init__(self, auth_lib, *, _context=None):
        super().__init__(auth_lib, _context=_context)
        self._updater_thread = None
        self._subscribers = []

    _worker_loop_interval = 5  # seconds between passes

    async def update(self, sensor: Sensor) -> Sensor:
        # Get updated device_params
        async with self._context.update_lock:
            sensor.device_params = await self.get_updated_params(sensor.mac)

        # Known types read cached device_params to avoid extra API calls.
        if sensor.type is DeviceTypes.TEMPERATURE_HUMIDITY:
            return sensor
        if (key := _STATE_KEYS.get(sensor.type)) is not None:
            sensor.detected = sensor.device_params.get(key) == 1
            return sensor

        properties = await self._get_device_info(sensor)

        for property in properties["data"]["property_list"]:
            pid = property["pid"]
            value = property["value"]

            try:
                if PropertyIDs(pid) == PropertyIDs.CONTACT_STATE:
                    sensor.detected = value == "1"
                if PropertyIDs(pid) == PropertyIDs.MOTION_STATE:
                    sensor.detected = value == "1"
            except ValueError:
                pass

        return sensor

    async def register_for_updates(
        self, sensor: Sensor, callback: Callable[[Sensor], None]
    ):
        _LOGGER.debug(f"Registering sensor: {sensor.nickname} for updates")
        self._context.check_ready()
        loop = asyncio.get_running_loop()
        if not self._updater_thread:
            self._updater_thread = Thread(
                target=self.update_worker,
                args=[
                    loop,
                ],
                daemon=True,
            )
            self._updater_thread.start()

        self._subscribers.append((sensor, callback))

    async def deregister_for_updates(self, sensor: Sensor):
        self._subscribers = [
            (sense, callback)
            for sense, callback in self._subscribers
            if sense.mac != sensor.mac
        ]

    def update_worker(self, loop):
        while True:
            for sensor, callback in self._subscribers:
                _LOGGER.debug(f"Providing update for {sensor.nickname}")
                try:
                    callback(
                        asyncio.run_coroutine_threadsafe(
                            self.update(sensor), loop
                        ).result()
                    )
                except _AuthenticationInProgress:
                    pass
                except UnknownApiError as e:
                    _LOGGER.warning(
                        f"The update method detected an UnknownApiError: {e}"
                    )
                except ClientOSError as e:
                    _LOGGER.error(f"A network error was detected: {e}")
                except ContentTypeError as e:
                    _LOGGER.error(f"Server returned unexpected ContentType: {e}")

            time.sleep(self._worker_loop_interval)

    async def get_sensors(self) -> List[Sensor]:
        sensors = [
            Sensor(device.raw_dict)
            for device in await self._get_cached_devices()
            if device.type is DeviceTypes.MOTION_SENSOR
            or device.type is DeviceTypes.CONTACT_SENSOR
            or device.type is DeviceTypes.LEAK_SENSOR
            or device.type is DeviceTypes.TEMPERATURE_HUMIDITY
        ]
        return [Sensor(sensor.raw_dict) for sensor in sensors]
