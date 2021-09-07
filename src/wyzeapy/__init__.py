#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import time
from typing import Dict, Any, List, Optional, Set
from inspect import iscoroutinefunction

from wyzeapy.const import PHONE_SYSTEM_TYPE, APP_VERSION, SC, APP_VER, SV, PHONE_ID, APP_NAME, OLIVE_APP_ID, APP_INFO
from wyzeapy.crypto import olive_create_signature
from wyzeapy.payload_factory import olive_create_user_info_payload
from wyzeapy.services.base_service import BaseService
from wyzeapy.services.bulb_service import BulbService
from wyzeapy.services.camera_service import CameraService
from wyzeapy.services.hms_service import HMSService
from wyzeapy.services.lock_service import LockService
from wyzeapy.services.sensor_service import SensorService
from wyzeapy.services.switch_service import SwitchService
from wyzeapy.services.thermostat_service import ThermostatService
from wyzeapy.utils import check_for_errors_standard
from wyzeapy.wyze_auth_lib import WyzeAuthLib, Token
from wyzeapy.exceptions import TwoFactorAuthenticationEnabled

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
        self._service: Optional[BaseService] = None
        self._token_callbacks: List[function] = []

    @classmethod
    async def create(cls):
        """
        Creates the Wyzeapy class in an async way. Although this is not currently utilized

        :return: An instance of the Wyzeapy class
        """
        self = cls()
        return self

    async def login(self, email, password, token: Token = None):
        """
        Logs the user in and retrieves the users token

        :param email: Users email
        :param password: Users password
        :param token: Users existing token from a previous session

        :raises:
            TwoFactorAuthenticationEnabled: indicates that the account has 2fa enabled
        """

        self._email = email
        self._password = password
        try:
            if token:
                # User token supplied, lets go ahead and use it and refresh the access token if needed.
                self._auth_lib = await WyzeAuthLib.create(email, password, token, token_callback=self.execute_token_callbacks)
                await self._auth_lib.refresh_if_should()
                self._service = BaseService(self._auth_lib)
            else:
                self._auth_lib = await WyzeAuthLib.create(email, password, token_callback=self.execute_token_callbacks)
                await self._auth_lib.get_token_with_username_password(email, password)
                self._service = BaseService(self._auth_lib)
        except TwoFactorAuthenticationEnabled as error:
            raise error

    async def login_with_2fa(self, verification_code) -> Token:
        """
        Logs the user in and retrieves the users token

        :param verification_code: Users 2fa verification code

        """

        _LOGGER.debug(f"Verification Code: {verification_code}")

        await self._auth_lib.get_token_with_2fa(verification_code)
        self._service = BaseService(self._auth_lib)
        return self._auth_lib.token

    async def execute_token_callbacks(self, token: Token):
        """
        Sends the token to the registered callback functions.

        :param token: Users token object

        """
        for callback in self._token_callbacks:
            if iscoroutinefunction(callback):
                await callback(token)
            else:
                callback(token)

    def register_for_token_callback(self, callback_function):
        """
        Register a callback to be called whenever the user's token is modified

        :param callback_function: A callback function which expects a token object

        """
        self._token_callbacks.append(callback_function)

    def unregister_for_token_callback(self, callback_function):
        """
        Register a callback to be called whenever the user's token is modified

        :param callback_function: A callback function which expects a token object

        """
        self._token_callbacks.remove(callback_function)

    @property
    async def unique_device_ids(self) -> Set[str]:
        """
        Returns a list of all device ids known to the server
        :return: A set containing the unique device ids
        """

        devices = await self._service.get_object_list()
        device_ids = set()
        for device in devices:
            device_ids.add(device.mac)

        return device_ids

    @property
    async def notifications_are_on(self) -> bool:
        """
        Reports the status of the notifications

        :return: True if the notifications are enabled
        """

        response_json = await self._service.get_user_profile()
        return response_json['data']['notification']

    async def enable_notifications(self):
        """Enables notifications on the account"""

        await self._service.set_push_info(True)

    async def disable_notifications(self):
        """Disables notifications on the account"""

        await self._service.set_push_info(False)

    @classmethod
    async def valid_login(cls, email: str, password: str) -> bool:
        """
        Checks to see if a username and password return a valid login

        :param email: The users email
        :param password: The users password
        :return: True if the account can connect
        """

        self = cls()
        await self.login(email, password)
        return not self._auth_lib.should_refresh

    @property
    async def bulb_service(self) -> BulbService:
        """Returns an instance of the bulb service"""

        if self._bulb_service is None:
            self._bulb_service = BulbService(self._auth_lib)
        return self._bulb_service

    @property
    async def switch_service(self) -> SwitchService:
        """Returns an instance of the switch service"""

        if self._switch_service is None:
            self._switch_service = SwitchService(self._auth_lib)
        return self._switch_service

    @property
    async def camera_service(self) -> CameraService:
        """Returns an instance of the camera service"""

        if self._camera_service is None:
            self._camera_service = CameraService(self._auth_lib)
        return self._camera_service

    @property
    async def thermostat_service(self) -> ThermostatService:
        """Returns an instance of the thermostat service"""

        if self._thermostat_service is None:
            self._thermostat_service = ThermostatService(self._auth_lib)
        return self._thermostat_service

    @property
    async def hms_service(self) -> HMSService:
        """Returns an instance of the hms service"""

        if self._hms_service is None:
            self._hms_service = await HMSService.create(self._auth_lib)
        return self._hms_service

    @property
    async def lock_service(self) -> LockService:
        """Returns an instance of the lock service"""

        if self._lock_service is None:
            self._lock_service = LockService(self._auth_lib)
        return self._lock_service

    @property
    async def sensor_service(self) -> SensorService:
        """Returns an instance of the sensor service"""

        if self._sensor_service is None:
            self._sensor_service = SensorService(self._auth_lib)
        return self._sensor_service
