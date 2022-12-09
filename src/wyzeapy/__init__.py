#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
from inspect import iscoroutinefunction
from typing import List, Optional, Set, Callable

from .const import PHONE_ID, OLIVE_APP_ID
from .crypto import olive_create_signature
from .exceptions import TwoFactorAuthenticationEnabled
from .payload_factory import olive_create_user_info_payload
from .services.base_service import BaseService, RokuBaseService
from .services.bulb_service import BulbService, RokuBulbService
from .services.camera_service import CameraService, RokuCameraService
from .services.hms_service import HMSService, RokuHMSService
from .services.lock_service import LockService, RokuLockService
from .services.sensor_service import SensorService, RokuSensorService
from .services.switch_service import SwitchService, RokuSwitchService
from .services.thermostat_service import ThermostatService, RokuThermostatService
from .services.wall_switch_service import WallSwitchService, RokuWallSwitchService
from .utils import check_for_errors_standard
from .wyze_auth_lib import WyzeAuthLib, Token, RokuAuthLib

_LOGGER = logging.getLogger(__name__)


class Wyzeapy:
    """A module to assist developers in interacting with the Wyze service"""
    _auth_lib: WyzeAuthLib
    _auth_lib_type = WyzeAuthLib
    _base_service_type = BaseService
    _bulb_service_type = BulbService
    _switch_service_type = SwitchService
    _camera_service_type = CameraService
    _thermostat_service_type = ThermostatService
    _hms_service_type = HMSService
    _lock_service_type = LockService
    _sensor_service_type = SensorService
    _wall_switch_service_type = WallSwitchService

    def __init__(self):
        self._bulb_service = None
        self._switch_service = None
        self._camera_service = None
        self._thermostat_service = None
        self._hms_service = None
        self._lock_service = None
        self._sensor_service = None
        self._wall_switch_service = None
        self._email = None
        self._password = None
        self._service: Optional[BaseService] = None
        self._token_callbacks: List[Callable] = []

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
                self._auth_lib = await self._auth_lib_type.create(
                    email, password, token, token_callback=self.execute_token_callbacks)
                await self._auth_lib.refresh_if_should()
                self._service = self._base_service_type(self._auth_lib)
            else:
                self._auth_lib = await self._auth_lib_type.create(
                    email, password, token_callback=self.execute_token_callbacks
                )
                await self._auth_lib.get_token_with_username_password(email, password)
                self._service = self._base_service_type(self._auth_lib)
        except TwoFactorAuthenticationEnabled as error:
            raise error

    async def login_with_2fa(self, verification_code) -> Token:
        """
        Logs the user in and retrieves the users token

        :param verification_code: Users 2fa verification code

        """

        _LOGGER.debug(f"Verification Code: {verification_code}")

        await self._auth_lib.get_token_with_2fa(verification_code)
        self._service = self._base_service_type(self._auth_lib)
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
            self._bulb_service = self._bulb_service_type(self._auth_lib)
        return self._bulb_service

    @property
    async def switch_service(self) -> SwitchService:
        """Returns an instance of the switch service"""

        if self._switch_service is None:
            self._switch_service = self._switch_service_type(self._auth_lib)
        return self._switch_service

    @property
    async def camera_service(self) -> CameraService:
        """Returns an instance of the camera service"""

        if self._camera_service is None:
            self._camera_service = self._camera_service_type(self._auth_lib)
        return self._camera_service

    @property
    async def thermostat_service(self) -> ThermostatService:
        """Returns an instance of the thermostat service"""

        if self._thermostat_service is None:
            self._thermostat_service = self._thermostat_service_type(self._auth_lib)
        return self._thermostat_service

    @property
    async def hms_service(self) -> HMSService:
        """Returns an instance of the hms service"""

        if self._hms_service is None:
            self._hms_service = await self._hms_service_type.create(self._auth_lib)
        return self._hms_service

    @property
    async def lock_service(self) -> LockService:
        """Returns an instance of the lock service"""

        if self._lock_service is None:
            self._lock_service = self._lock_service_type(self._auth_lib)
        return self._lock_service

    @property
    async def sensor_service(self) -> SensorService:
        """Returns an instance of the sensor service"""

        if self._sensor_service is None:
            self._sensor_service = self._sensor_service_type(self._auth_lib)
        return self._sensor_service

    @property
    async def wall_switch_service(self) -> WallSwitchService:
        """Returns an instance of the switch service"""

        if self._wall_switch_service is None:
            self._wall_switch_service = self._wall_switch_service_type(self._auth_lib)
        return self._wall_switch_service


class Rokuapy(Wyzeapy):
    _auth_lib: RokuAuthLib
    _auth_lib_type = RokuAuthLib
    _base_service_type = RokuBaseService
    _bulb_service_type = RokuBulbService
    _switch_service_type = RokuSwitchService
    _camera_service_type = RokuCameraService
    _thermostat_service_type = RokuThermostatService
    _hms_service_type = RokuHMSService
    _lock_service_type = RokuLockService
    _sensor_service_type = RokuSensorService
    _wall_switch_service_type = RokuWallSwitchService
