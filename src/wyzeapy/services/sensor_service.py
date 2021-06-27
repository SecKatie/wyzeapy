#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import asyncio
import time
from threading import Thread
from typing import List, Callable, Tuple, Optional

from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, PropertyIDs


class Sensor(Device):
    detected: bool = False


class SensorService(BaseService):
    _updater_thread: Optional[Thread]
    _subscribers: List[Tuple[Sensor, Callable[[Sensor], None]]] = []

    async def update(self, sensor: Sensor) -> Sensor:
        properties = await self._client.net_client.get_device_info(sensor)

        for property in properties['data']['property_list']:
            pid = property['pid']
            value = property['value']

            try:
                if PropertyIDs(pid) == PropertyIDs.CONTACT_STATE:
                    sensor.detected = value == "1"
                if PropertyIDs(pid) == PropertyIDs.MOTION_STATE:
                    sensor.detected = value == "1"
            except ValueError:
                pass

        return sensor


    async def register_for_updates(self, sensor: Sensor, callback: Callable[[Sensor], None]):
        if self._updater_thread is None:
            self._updater_thread = Thread(target=self.update_worker, daemon=True)

        self._subscribers.append((sensor, callback))

    def update_worker(self):
        loop = asyncio.get_event_loop()
        while True:
            if len(self._subscribers) < 1:
                time.sleep(0.1)
            else:
                for sensor, callback in self._subscribers:
                    callback(asyncio.run_coroutine_threadsafe(self.update(sensor), loop).result())

    async def get_sensors(self) -> List[Sensor]:
        return [Sensor(sensor.raw_dict) for sensor in await self._client.get_sensors()]
