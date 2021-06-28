#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from typing import Dict

from wyzeapy.client import Client
from wyzeapy.services.bulb_service import BulbService
from wyzeapy.services.camera_service import CameraService
from wyzeapy.services.hms_service import HMSService
from wyzeapy.services.lock_service import LockService
from wyzeapy.services.sensor_service import SensorService
from wyzeapy.services.switch_service import SwitchService
from wyzeapy.services.thermostat_service import ThermostatService


class Wyzeapy:
    _client: Client

    def __init__(self):
        self._token: Dict[str, str] = {}
        self._bulb_service = None
        self._switch_service = None
        self._camera_service = None
        self._thermostat_service = None
        self._hms_service = None
        self._lock_service = None

    @classmethod
    async def create(cls):
        self = Wyzeapy()
        self._client = Client("", "")
        return self

    async def async_close(self):
        await self._client.async_close()

    async def login(self, email, password):
        self._client.email = email
        self._client.password = password
        await self._client.async_init()
        self._token['access_token'] = self._client.net_client.access_token
        self._token['refresh_token'] = self._client.net_client.refresh_token

    @property
    async def valid_login(self):
        return self._client.valid_login

    @property
    async def bulb_service(self) -> BulbService:
        if self._bulb_service is None:
            self._bulb_service = BulbService(self._client)
        return self._bulb_service

    @property
    async def switch_service(self) -> SwitchService:
        if self._lock_service is None:
            self._lock_service = SwitchService(self._client)
        return self._lock_service

    @property
    async def camera_service(self) -> CameraService:
        if self._camera_service is None:
            self._camera_service = CameraService(self._client)
        return self._camera_service

    @property
    async def thermostat_service(self) -> ThermostatService:
        if self._thermostat_service is None:
            self._thermostat_service = ThermostatService(self._client)
        return self._thermostat_service

    @property
    async def hms_service(self) -> HMSService:
        if self._hms_service is None:
            self._hms_service = HMSService(self._client)
        return self._hms_service

    @property
    async def lock_service(self) -> LockService:
        if self._lock_service is None:
            self._lock_service = LockService(self._client)
        return self._lock_service
