#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import time
from typing import Dict, Any

from wyzeapy.const import PHONE_SYSTEM_TYPE, APP_VERSION, SC, APP_VER, SV, PHONE_ID, APP_NAME, OLIVE_APP_ID, APP_INFO
from wyzeapy.crypto import olive_create_signature
from wyzeapy.payload_factory import olive_create_user_info_payload
from wyzeapy.services.bulb_service import BulbService
from wyzeapy.services.camera_service import CameraService
from wyzeapy.services.hms_service import HMSService
from wyzeapy.services.lock_service import LockService
from wyzeapy.services.sensor_service import SensorService
from wyzeapy.services.switch_service import SwitchService
from wyzeapy.services.thermostat_service import ThermostatService
from wyzeapy.utils import check_for_errors_standard
from wyzeapy.wyze_auth_lib import WyzeAuthLib

_LOGGER = logging.getLogger(__name__)


class Wyzeapy:
    """A module to assist developers in interacting with the Wyze service"""
    # _client: Client
    _auth_lib: WyzeAuthLib

    def __init__(self):
        self._bulb_service = None
        self._switch_service = None
        self._camera_service = None
        self._thermostat_service = None
        self._hms_service = None
        self._lock_service = None
        self._sensor_service = None
        self._email = None
        self._password = None

    @classmethod
    async def create(cls):
        """
        Creates the Wyzeapy class

        :return: An instance of the Wyzeapy class
        """
        self = cls()
        return self

    async def async_close(self):
        # await self._client.async_close()
        await self._auth_lib.close()

    async def login(self, email, password):
        _LOGGER.debug(f"Email: {email}")
        self._email = email
        _LOGGER.debug(f"Password: {password}")
        self._password = password
        self._auth_lib = await WyzeAuthLib.create(email, password)

    @property
    async def notifications_are_on(self) -> bool:
        response_json = await self._get_user_profile()
        return response_json['data']['notification']

    async def _get_user_profile(self) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        payload = olive_create_user_info_payload()
        signature = olive_create_signature(payload, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        url = 'https://wyze-platform-service.wyzecam.com/app/v2/platform/get_user_profile'

        response_json = await self._auth_lib.get(url, headers=headers, params=payload)

        return response_json

    async def enable_notifications(self):
        await self._set_push_info(True)

    async def disable_notifications(self):
        await self._set_push_info(False)

    async def _set_push_info(self, on: bool) -> None:
        await self._auth_lib.refresh_if_should()

        url = "https://api.wyzecam.com/app/user/set_push_info"
        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "push_switch": "1" if on else "2",
            "sc": SC,
            "ts": int(time.time()),
            "sv": SV,
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        response_json = await self._auth_lib.post(url, json=payload)

        check_for_errors_standard(response_json)

    @classmethod
    async def valid_login(cls, email: str, password: str) -> bool:
        self = cls()
        await self.login(email, password)
        return not self._auth_lib.should_refresh

    @property
    async def bulb_service(self) -> BulbService:
        if self._bulb_service is None:
            self._bulb_service = BulbService(self._auth_lib)
        return self._bulb_service

    @property
    async def switch_service(self) -> SwitchService:
        if self._switch_service is None:
            self._switch_service = SwitchService(self._auth_lib)
        return self._switch_service

    @property
    async def camera_service(self) -> CameraService:
        if self._camera_service is None:
            self._camera_service = CameraService(self._auth_lib)
        return self._camera_service

    @property
    async def thermostat_service(self) -> ThermostatService:
        if self._thermostat_service is None:
            self._thermostat_service = ThermostatService(self._auth_lib)
        return self._thermostat_service

    @property
    async def hms_service(self) -> HMSService:
        if self._hms_service is None:
            self._hms_service = await HMSService.create(self._auth_lib)
        return self._hms_service

    @property
    async def lock_service(self) -> LockService:
        if self._lock_service is None:
            self._lock_service = LockService(self._auth_lib)
        return self._lock_service

    @property
    async def sensor_service(self) -> SensorService:
        if self._sensor_service is None:
            self._sensor_service = SensorService(self._auth_lib)
        return self._sensor_service
