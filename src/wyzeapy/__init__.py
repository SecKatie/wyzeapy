#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import logging
from inspect import iscoroutinefunction
from typing import List, Optional, Set, Callable

from .exceptions import TwoFactorAuthenticationEnabled
from .services.base_service import BaseService
from .services.bulb_service import BulbService
from .services.camera_service import CameraService
from .services.hms_service import HMSService
from .services.lock_service import LockService
from .services.sensor_service import SensorService
from .services.switch_service import SwitchService, SwitchUsageService
from .services.thermostat_service import ThermostatService
from .services.wall_switch_service import WallSwitchService
from .wyze_auth_lib import WyzeAuthLib, Token

_LOGGER = logging.getLogger(__name__)


class Wyzeapy:
    """A Python module to assist developers in interacting with the Wyze service API.
    
    This class provides methods for authentication, device management, and accessing
    various Wyze device services including:
    
    * **Bulbs** - Control brightness, color, and power state
    * **Switches** - Toggle power and monitor usage
    * **Cameras** - Access video streams and control settings
    * **Thermostats** - Manage temperature settings and modes
    * **Locks** - Control and monitor door locks
    * **Sensors** - Monitor motion, contact, and environmental sensors
    * **HMS** - Manage home monitoring system
    
    Most interactions with Wyze devices should go through this class.
    """
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
        self._wall_switch_service = None
        self._switch_usage_service = None
        self._email = None
        self._password = None
        self._key_id = None
        self._api_key = None
        self._service: Optional[BaseService] = None
        self._token_callbacks: List[Callable] = []

    @classmethod
    async def create(cls):
        """
        Creates and initializes the Wyzeapy class asynchronously.
        
        This factory method provides a way to instantiate the class using async/await syntax,
        though it's currently a simple implementation that may be expanded in the future.
        
        **Returns:**
            `Wyzeapy`: A new instance of the Wyzeapy class ready for authentication.
        """
        self = cls()
        return self

    async def login(
        self, email, password, key_id, api_key, token: Optional[Token] = None
    ):
        """
        Authenticates with the Wyze API and retrieves the user's access token.
        
        This method handles the authentication process, including token management
        and service initialization. If two-factor authentication is enabled on the account,
        it will raise an exception requiring the use of `login_with_2fa()` instead.
        
        **Args:**
        * `email` (str): User's email address for Wyze account
        * `password` (str): User's password for Wyze account
        * `key_id` (str): Key ID for third-party API access
        * `api_key` (str): API Key for third-party API access
        * `token` (Optional[Token], optional): Existing token from a previous session. Defaults to None.
        
        **Raises:**
        * `TwoFactorAuthenticationEnabled`: When the account has 2FA enabled and requires verification
        """

        self._email = email
        self._password = password
        self._key_id = key_id
        self._api_key = api_key

        try:
            self._auth_lib = await WyzeAuthLib.create(
                email, password, key_id, api_key, token, self.execute_token_callbacks
            )
            if token:
                # User token supplied, refresh on startup
                await self._auth_lib.refresh()
            else:
                await self._auth_lib.get_token_with_username_password(
                    email, password, key_id, api_key
                )
            self._service = BaseService(self._auth_lib)
        except TwoFactorAuthenticationEnabled as error:
            raise error

    async def login_with_2fa(self, verification_code) -> Token:
        """
        Completes the login process for accounts with two-factor authentication enabled.
        
        This method should be called after receiving a `TwoFactorAuthenticationEnabled`
        exception from the `login()` method. It completes the authentication process
        using the verification code sent to the user.
        
        **Args:**
        * `verification_code` (str): The 2FA verification code received by the user
            
        **Returns:**
        * `Token`: The authenticated user token object
        """

        _LOGGER.debug(f"Verification Code: {verification_code}")

        await self._auth_lib.get_token_with_2fa(verification_code)
        self._service = BaseService(self._auth_lib)
        return self._auth_lib.token

    async def execute_token_callbacks(self, token: Token):
        """
        Sends the token to all registered callback functions.
        
        This method is called internally whenever the token is refreshed or updated,
        allowing external components to stay in sync with token changes.
        
        **Args:**
        * `token` (Token): The current user token object
        """
        for callback in self._token_callbacks:
            if iscoroutinefunction(callback):
                await callback(token)
            else:
                callback(token)

    def register_for_token_callback(self, callback_function):
        """
        Registers a callback function to be called whenever the user's token is modified.
        
        This allows external components to be notified of token changes for persistence
        or other token-dependent operations.
        
        **Args:**
        * `callback_function`: A function that accepts a Token object as its parameter
        
        **Example:**
        ```python
        def token_updated(token):
            print(f"Token refreshed: {token.access_token[:10]}...")
            
        wyze = Wyzeapy()
        wyze.register_for_token_callback(token_updated)
        ```
        """
        self._token_callbacks.append(callback_function)

    def unregister_for_token_callback(self, callback_function):
        """
        Removes a previously registered token callback function.
        
        This stops the specified callback from receiving token updates.
        
        **Args:**
        * `callback_function`: The callback function to remove from the notification list
        """
        self._token_callbacks.remove(callback_function)

    @property
    async def unique_device_ids(self) -> Set[str]:
        """
        Retrieves a set of all unique device IDs known to the Wyze server.
        
        This property fetches all devices associated with the account and
        extracts their MAC addresses as unique identifiers.
        
        **Returns:**
        * `Set[str]`: A set containing all unique device IDs (MAC addresses)
        
        **Example:**
        ```python
        device_ids = await wyze.unique_device_ids
        print(f"Found {len(device_ids)} devices")
        ```
        """

        devices = await self._service.get_object_list()
        device_ids = set()
        for device in devices:
            device_ids.add(device.mac)

        return device_ids

    @property
    async def notifications_are_on(self) -> bool:
        """
        Checks if push notifications are enabled for the account.
        
        This property queries the user profile to determine the current
        notification settings status.
        
        **Returns:**
        * `bool`: True if notifications are enabled, False otherwise
        """

        response_json = await self._service.get_user_profile()
        return response_json['data']['notification']

    async def enable_notifications(self):
        """Enables push notifications for the Wyze account.
        
        This method updates the user's profile to turn on push notifications
        for all supported devices and events.
        
        **Example:**
        ```python
        # Turn on notifications
        await wyze.enable_notifications()
        ```
        """

        await self._service.set_push_info(True)

    async def disable_notifications(self):
        """Disables push notifications for the Wyze account.
        
        This method updates the user's profile to turn off push notifications
        for all devices and events.
        
        **Example:**
        ```python
        # Turn off notifications
        await wyze.disable_notifications()
        ```
        """

        await self._service.set_push_info(False)

    @classmethod
    async def valid_login(
        cls, email: str, password: str, key_id: str, api_key: str
    ) -> bool:
        """
        Validates if the provided credentials can successfully authenticate with the Wyze API.
        
        This method attempts to log in with the provided credentials and returns whether
        the authentication was successful. It's useful for validating credentials without
        needing to handle the full login process.
        
        **Args:**
        * `email` (str): The user's email address
        * `password` (str): The user's password
        * `key_id` (str): Key ID for third-party API access
        * `api_key` (str): API Key for third-party API access
            
        **Returns:**
        * `bool`: True if the credentials are valid and authentication succeeded
        
        **Example:**
        ```python
        is_valid = await Wyzeapy.valid_login("user@example.com", "password123", "key_id", "api_key")
        if is_valid:
            print("Credentials are valid")
        else:
            print("Invalid credentials")
        ```
        """

        self = cls()
        await self.login(email, password, key_id, api_key)

        return not self._auth_lib.should_refresh

    @property
    async def bulb_service(self) -> BulbService:
        """Provides access to the Wyze Bulb service.
        
        This property lazily initializes and returns a BulbService instance
        for controlling and monitoring Wyze bulbs.
        
        **Returns:**
        * `BulbService`: An instance of the bulb service for interacting with Wyze bulbs
        
        **Example:**
        ```python
        # Get all bulbs
        bulb_service = await wyze.bulb_service
        bulbs = await bulb_service.get_bulbs()
        ```
        """

        if self._bulb_service is None:
            self._bulb_service = BulbService(self._auth_lib)
        return self._bulb_service

    @property
    async def switch_service(self) -> SwitchService:
        """Provides access to the Wyze Switch service.
        
        This property lazily initializes and returns a SwitchService instance
        for controlling and monitoring Wyze plugs and switches.
        
        **Returns:**
        * `SwitchService`: An instance of the switch service for interacting with Wyze switches
        
        **Example:**
        ```python
        # Get all switches
        switch_service = await wyze.switch_service
        switches = await switch_service.get_switches()
        ```
        """

        if self._switch_service is None:
            self._switch_service = SwitchService(self._auth_lib)
        return self._switch_service

    @property
    async def camera_service(self) -> CameraService:
        """Provides access to the Wyze Camera service.
        
        This property lazily initializes and returns a CameraService instance
        for controlling and monitoring Wyze cameras.
        
        **Returns:**
        * `CameraService`: An instance of the camera service for interacting with Wyze cameras
        
        **Example:**
        ```python
        # Get all cameras
        camera_service = await wyze.camera_service
        cameras = await camera_service.get_cameras()
        ```
        """

        if self._camera_service is None:
            self._camera_service = CameraService(self._auth_lib)
        return self._camera_service

    @property
    async def thermostat_service(self) -> ThermostatService:
        """Provides access to the Wyze Thermostat service.
        
        This property lazily initializes and returns a ThermostatService instance
        for controlling and monitoring Wyze thermostats.
        
        **Returns:**
        * `ThermostatService`: An instance of the thermostat service for interacting with Wyze thermostats
        
        **Example:**
        ```python
        # Get all thermostats
        thermostat_service = await wyze.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        ```
        """

        if self._thermostat_service is None:
            self._thermostat_service = ThermostatService(self._auth_lib)
        return self._thermostat_service

    @property
    async def hms_service(self) -> HMSService:
        """Provides access to the Wyze Home Monitoring Service (HMS).
        
        This property lazily initializes and returns an HMSService instance
        for controlling and monitoring the Wyze home security system.
        
        **Returns:**
        * `HMSService`: An instance of the HMS service for interacting with Wyze home monitoring
        
        **Example:**
        ```python
        # Get HMS status
        hms_service = await wyze.hms_service
        status = await hms_service.get_hms_status()
        ```
        """

        if self._hms_service is None:
            self._hms_service = await HMSService.create(self._auth_lib)
        return self._hms_service

    @property
    async def lock_service(self) -> LockService:
        """Provides access to the Wyze Lock service.
        
        This property lazily initializes and returns a LockService instance
        for controlling and monitoring Wyze locks.
        
        **Returns:**
        * `LockService`: An instance of the lock service for interacting with Wyze locks
        
        **Example:**
        ```python
        # Get all locks
        lock_service = await wyze.lock_service
        locks = await lock_service.get_locks()
        ```
        """

        if self._lock_service is None:
            self._lock_service = LockService(self._auth_lib)
        return self._lock_service

    @property
    async def sensor_service(self) -> SensorService:
        """Provides access to the Wyze Sensor service.
        
        This property lazily initializes and returns a SensorService instance
        for monitoring Wyze sensors such as contact sensors, motion sensors, etc.
        
        **Returns:**
        * `SensorService`: An instance of the sensor service for interacting with Wyze sensors
        
        **Example:**
        ```python
        # Get all sensors
        sensor_service = await wyze.sensor_service
        sensors = await sensor_service.get_sensors()
        ```
        """

        if self._sensor_service is None:
            self._sensor_service = SensorService(self._auth_lib)
        return self._sensor_service

    @property
    async def wall_switch_service(self) -> WallSwitchService:
        """Provides access to the Wyze Wall Switch service.
        
        This property lazily initializes and returns a WallSwitchService instance
        for controlling and monitoring Wyze wall switches.
        
        **Returns:**
        * `WallSwitchService`: An instance of the wall switch service for interacting with Wyze wall switches
        
        **Example:**
        ```python
        # Get all wall switches
        wall_switch_service = await wyze.wall_switch_service
        switches = await wall_switch_service.get_wall_switches()
        ```
        """

        if self._wall_switch_service is None:
            self._wall_switch_service = WallSwitchService(self._auth_lib)
        return self._wall_switch_service

    @property
    async def switch_usage_service(self) -> SwitchUsageService:
        """Provides access to the Wyze Switch Usage service.
        
        This property lazily initializes and returns a SwitchUsageService instance
        for retrieving usage statistics from Wyze switches and plugs.
        
        **Returns:**
        * `SwitchUsageService`: An instance of the switch usage service for accessing Wyze switch usage data
        
        **Example:**
        ```python
        # Get usage data for a switch
        usage_service = await wyze.switch_usage_service
        usage = await usage_service.get_usage_records(switch_mac)
        ```
        """
        if self._switch_usage_service is None:
            self._switch_usage_service = SwitchUsageService(self._auth_lib)
        return self._switch_usage_service
