"""
Wyzeapy - A Python wrapper for the Wyze API.

This module provides a high-level async interface for interacting with Wyze smart home devices.
"""

from __future__ import annotations

import time
import uuid
from typing import Awaitable, Callable, Optional, Union

from .wyze_api_client.api.user import get_user_profile

from .devices import create_device, WyzeDevice
from .models import (
    CameraEvent,
    PlugUsageRecord,
    LockInfo,
    ThermostatState,
    IrrigationZone,
    Token,
    WyzeUser,
)
from .services.hms import WyzeHMS
from .exceptions import (
    AuthenticationError,
    TwoFactorAuthRequired,
    TokenRefreshError,
    NotAuthenticatedError,
)
from .utils import hash_password, ford_create_signature, olive_create_signature
from .const import (
    AUTH_SERVER,
    MAIN_API_SERVER,
    LOCK_API_SERVER,
    PLATFORM_SERVICE_URL,
    DEVICEMGMT_SERVICE_URL,
    PHONE_SYSTEM_TYPE,
    APP_VERSION,
    APP_VER,
    APP_NAME,
    SC,
    SV,
    APP_INFO,
    FORD_APP_KEY,
    OLIVE_APP_ID,
    PropertyID,
    DEVICEMGMT_API_MODELS,
)

from .wyze_api_client import Client, AuthenticatedClient
from .wyze_api_client.api.authentication import (
    login_with_credentials,
    login_with_2fa,
    refresh_token,
)
from .wyze_api_client.api.devices import (
    get_object_list,
    run_action,
    set_property,
    get_device_info,
    get_property_list,
)
from .wyze_api_client.api.camera import get_event_list, device_mgmt_run_action
from .wyze_api_client.api.switch import get_plug_usage_history
from .wyze_api_client.api.lock import lock_control, get_lock_info
from .wyze_api_client.api.thermostat import get_thermostat_iot_prop, set_thermostat_iot_prop
from .wyze_api_client.api.irrigation import (
    get_irrigation_zones,
    irrigation_quick_run,
    stop_irrigation_schedule,
)
from .wyze_api_client.models import (
    LoginRequest,
    RunActionRequestActionParams,
    TwoFactorLoginRequest,
    TwoFactorLoginRequestMfaType,
    CommonRequestParams,
    RunActionRequest,
    RunActionRequestActionKey,
    SetPropertyRequest,
    LockControlRequest,
    LockControlRequestAction,
    RefreshTokenRequest,
    GetDeviceInfoBody,
    GetPropertyListRequest,
    GetEventListBody,
    PlugUsageRequest,
    SetThermostatIotPropBody,
    SetThermostatIotPropBodyProps,
    IrrigationQuickRunRequest,
    IrrigationQuickRunRequestZoneRunsItem,
    IrrigationStopRequest,
    IrrigationStopRequestAction,
    DeviceMgmtRunActionRequest,
    DeviceMgmtRunActionRequestTargetInfo,
    DeviceMgmtRunActionRequestTargetInfoType,
    DeviceMgmtRunActionRequestCapabilitiesItem,
    DeviceMgmtRunActionRequestCapabilitiesItemName,
    DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem,
)
from .wyze_api_client.types import Unset


# Type alias for 2FA callback: receives auth_type ("TOTP" or "SMS"), returns verification code
TwoFactorCallback = Callable[[str], Union[str, Awaitable[str]]]


class Wyzeapy:
    """
    High-level async interface for the Wyze API.

    Example:
        ```python
        async with Wyzeapy("email@example.com", "password", key_id, api_key) as wyze:
            devices = await wyze.list_devices()
            for device in devices:
                print(f"{device.nickname}: {device.product_model}")

            # Control devices directly
            for device in devices:
                if isinstance(device, WyzeLight):
                    await device.turn_on()
                    await device.set_brightness(75)
                elif isinstance(device, WyzeLock):
                    await device.lock()
        ```

    With 2FA:
        ```python
        def get_2fa_code(auth_type: str) -> str:
            return input(f"Enter {auth_type} code: ")

        async with Wyzeapy(email, password, key_id, api_key, tfa_callback=get_2fa_code) as wyze:
            devices = await wyze.list_devices()
        ```
    """

    def __init__(
        self,
        email: str,
        password: str,
        key_id: str,
        api_key: str,
        tfa_callback: Optional[TwoFactorCallback] = None,
    ):
        self._email = email
        self._password_hash = hash_password(password)
        self._key_id = key_id
        self._api_key = api_key
        self._phone_id = str(uuid.uuid4())
        self._tfa_callback = tfa_callback

        self._token: Optional[Token] = None
        self._auth_client: Optional[Client] = None
        self._main_client: Optional[Client] = None
        self._devices: Optional[list[WyzeDevice]] = None
        self._hms: Optional[WyzeHMS] = None

        # Action keys for device control (accessed by device classes)
        self._action_power_on = RunActionRequestActionKey.POWER_ON
        self._action_power_off = RunActionRequestActionKey.POWER_OFF
        self._action_siren_on = RunActionRequestActionKey.SIREN_ON
        self._action_siren_off = RunActionRequestActionKey.SIREN_OFF
        self._lock_action_lock = LockControlRequestAction.REMOTELOCK
        self._lock_action_unlock = LockControlRequestAction.REMOTEUNLOCK

        # Property IDs for device control (accessed by device classes)
        self._prop_brightness = PropertyID.BRIGHTNESS
        self._prop_color_temp = PropertyID.COLOR_TEMP
        self._prop_color = PropertyID.COLOR
        self._prop_color_mode = PropertyID.COLOR_MODE

    async def __aenter__(self) -> "Wyzeapy":
        """Login and return self."""
        await self._login()
        return self

    async def __aexit__(self, *args) -> None:
        """Clean up HTTP clients."""
        if self._auth_client:
            await self._auth_client.get_async_httpx_client().aclose()
        if self._main_client:
            await self._main_client.get_async_httpx_client().aclose()

    def _get_auth_client(self) -> Client:
        if self._auth_client is None:
            self._auth_client = Client(base_url=AUTH_SERVER)
        return self._auth_client

    def _get_main_client(self) -> Client:
        if self._main_client is None:
            self._main_client = Client(base_url=MAIN_API_SERVER)
        return self._main_client

    async def _login(self) -> Token:
        """Authenticate with the Wyze API."""
        client = self._get_auth_client()

        result = await login_with_credentials.asyncio_detailed(
            client=client,
            body=LoginRequest(email=self._email, password=self._password_hash),
            keyid=self._key_id,
            apikey=self._api_key,
        )

        if result.status_code != 200:
            raise AuthenticationError(
                f"Login failed: {result.status_code} - {result.content.decode()}"
            )

        response = result.parsed
        if response is None:
            raise AuthenticationError(
                f"Login failed: could not parse response - {result.content.decode()}"
            )

        # Check for 2FA requirement
        if (
            not isinstance(response.mfa_options, Unset)
            and response.mfa_options is not None
        ):
            if "TotpVerificationCode" in response.mfa_options:
                if (
                    not isinstance(response.mfa_details, Unset)
                    and response.mfa_details is not None
                    and hasattr(response.mfa_details, "totp_apps")
                ):
                    totp_apps = response.mfa_details.additional_properties.get(
                        "totp_apps", []
                    )
                    if totp_apps:
                        return await self._handle_2fa(
                            "TOTP", totp_apps[0].get("app_id", "")
                        )
                raise AuthenticationError(
                    "TOTP 2FA required but no TOTP app configured"
                )

            if "PrimaryPhone" in response.mfa_options:
                if (
                    not isinstance(response.sms_session_id, Unset)
                    and response.sms_session_id is not None
                ):
                    return await self._handle_2fa("SMS", response.sms_session_id)
                raise AuthenticationError("SMS 2FA required but no session ID provided")

        if isinstance(response.access_token, Unset) or response.access_token is None:
            raise AuthenticationError(
                f"Login failed: {getattr(response, 'error_code', 'unknown error')}"
            )

        if isinstance(response.refresh_token, Unset) or response.refresh_token is None:
            raise AuthenticationError("Login failed: no refresh token received")

        self._token = Token(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
        )
        return self._token

    async def _handle_2fa(self, auth_type: str, verification_id: str) -> Token:
        """Handle two-factor authentication."""
        if self._tfa_callback is None:
            raise TwoFactorAuthRequired(auth_type)

        # Call the callback (may be sync or async)
        result = self._tfa_callback(auth_type)
        if isinstance(result, str):
            code = result
        else:
            code = await result

        client = self._get_auth_client()

        mfa_type = (
            TwoFactorLoginRequestMfaType.TOTPVERIFICATIONCODE
            if auth_type == "TOTP"
            else TwoFactorLoginRequestMfaType.PRIMARYPHONE
        )

        response = await login_with_2fa.asyncio(
            client=client,
            phone_id=self._phone_id,
            x_api_key=self._api_key,
            body=TwoFactorLoginRequest(
                email=self._email,
                password=self._password_hash,
                mfa_type=mfa_type,
                verification_id=verification_id,
                verification_code=code,
            ),
        )

        if response is None:
            raise AuthenticationError("2FA login failed")

        if isinstance(response.access_token, Unset) or response.access_token is None:
            raise AuthenticationError("2FA login failed: no access token")

        if isinstance(response.refresh_token, Unset) or response.refresh_token is None:
            raise AuthenticationError("2FA login failed: no refresh token")

        self._token = Token(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
        )
        return self._token

    def _get_token(self) -> Token:
        if self._token is None:
            raise NotAuthenticatedError("No token available")
        return self._token

    async def _refresh_token(self) -> Token:
        """Refresh the access token using the refresh token."""
        if self._token is None:
            raise NotAuthenticatedError("No token to refresh")

        client = self._get_main_client()

        response = await refresh_token.asyncio(
            client=client,
            body=RefreshTokenRequest(
                refresh_token=self._token.refresh_token,
                **self._common_params(),
            ),
        )

        if response is None:
            raise TokenRefreshError("Token refresh failed")

        if isinstance(response.data, Unset) or response.data is None:
            raise TokenRefreshError("Token refresh failed: no data in response")

        if (
            isinstance(response.data.access_token, Unset)
            or response.data.access_token is None
        ):
            raise TokenRefreshError("Token refresh failed: no access token")

        if (
            isinstance(response.data.refresh_token, Unset)
            or response.data.refresh_token is None
        ):
            raise TokenRefreshError("Token refresh failed: no refresh token")

        self._token = Token(
            access_token=response.data.access_token,
            refresh_token=response.data.refresh_token,
        )
        return self._token

    async def _ensure_token_valid(self) -> None:
        """Check if token needs refresh and refresh if necessary."""
        if self._token is None:
            raise NotAuthenticatedError("Not authenticated")

        if self._token.should_refresh:
            await self._refresh_token()

    def _common_params(self) -> dict:
        """Build common request parameters."""
        return {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "app_name": APP_NAME,
            "phone_id": self._phone_id,
            "sc": SC,
            "sv": SV,
            "ts": int(time.time()),
            "access_token": self._get_token().access_token,
        }

    @property
    def devices(self) -> list[WyzeDevice]:
        """
        Get cached devices. Returns empty list if not yet fetched.

        Use `list_devices()` to fetch devices from the API.
        """
        return self._devices or []

    @property
    def hms(self) -> WyzeHMS:
        """
        Access the Home Monitoring Service (HMS) API.

        Example:
            ```python
            async with Wyzeapy(email, password, key_id, api_key) as wyze:
                status = await wyze.hms.get_status("your-hms-id")
                await wyze.hms.set_mode("your-hms-id", HMSMode.AWAY)
            ```
        """
        if self._hms is None:
            self._hms = WyzeHMS(self)
        return self._hms

    async def list_devices(self, *, refresh: bool = False) -> list[WyzeDevice]:
        """
        Get all devices associated with the account.

        Devices are cached after the first fetch. Subsequent calls return
        the cached list unless `refresh=True` is specified.

        Args:
            refresh: If True, fetch fresh data from the API instead of
                    returning cached devices.

        Returns:
            List of Device objects with control methods available
        """
        if self._devices is not None and not refresh:
            return self._devices

        await self._ensure_token_valid()

        client = self._get_main_client()

        response = await get_object_list.asyncio(
            client=client,
            body=CommonRequestParams(**self._common_params()),
        )

        if (
            response is None
            or response.data is None
            or isinstance(response.data, Unset)
        ):
            self._devices = []
            return self._devices

        self._devices = [
            create_device(device, self) for device in response.data.device_list or []
        ]
        return self._devices

    async def get_user(self) -> WyzeUser:
        """
        Get the current user's profile.

        Returns:
            WyzeUser object with profile information
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))
        payload = {"nonce": nonce}
        signature = olive_create_signature(payload, access_token)

        # Create authenticated client for platform service
        platform_client = AuthenticatedClient(
            base_url=PLATFORM_SERVICE_URL,
            token=access_token,
            prefix="",  # No prefix, just the raw token
            auth_header_name="access_token",
        )

        try:
            response = await get_user_profile.asyncio(
                client=platform_client,
                nonce=nonce,
                appid=OLIVE_APP_ID,
                appinfo=APP_INFO,
                phoneid=self._phone_id,
                signature2=signature,
            )

            if response is None or isinstance(response.data, Unset):
                return WyzeUser()

            # Convert response data to dict to capture all properties
            data_dict = response.data.to_dict()
            return WyzeUser.from_response(data_dict)
        finally:
            await platform_client.get_async_httpx_client().aclose()

    # -------------------------------------------------------------------------
    # Internal API Methods (used by device classes)
    # -------------------------------------------------------------------------

    async def run_action(
        self, device: WyzeDevice, action: RunActionRequestActionKey
    ) -> bool:
        """Execute an action on a device."""
        await self._ensure_token_valid()

        client = self._get_main_client()

        response = await run_action.asyncio(
            client=client,
            body=RunActionRequest(
                provider_key=device.product_model or "",
                instance_id=device.mac or "",
                action_key=action,
                action_params=RunActionRequestActionParams(),
                custom_string="",
                **self._common_params(),
            ),
        )

        return response is not None and getattr(response, "code", None) == "1"

    async def set_property(
        self, device: WyzeDevice, property_id: str, value: str
    ) -> bool:
        """Set a property on a device."""
        await self._ensure_token_valid()

        client = self._get_main_client()

        response = await set_property.asyncio(
            client=client,
            body=SetPropertyRequest(
                device_mac=device.mac or "",
                device_model=device.product_model or "",
                pid=property_id,
                pvalue=value,
                **self._common_params(),
            ),
        )

        return response is not None and getattr(response, "code", None) == "1"

    async def _lock_control(
        self, device: WyzeDevice, action: LockControlRequestAction
    ) -> bool:
        """Control a lock device."""
        await self._ensure_token_valid()

        # Lock API requires its own client with different base URL
        lock_client = Client(base_url=LOCK_API_SERVER)

        try:
            timestamp = str(int(time.time() * 1000))
            device_uuid = device.mac or ""
            access_token = self._get_token().access_token

            # Build payload for signature
            payload = {
                "access_token": access_token,
                "action": action.value,
                "key": FORD_APP_KEY,
                "timestamp": timestamp,
                "uuid": device_uuid,
            }

            signature = ford_create_signature(
                "/openapi/lock/v1/control", "POST", payload
            )

            response = await lock_control.asyncio(
                client=lock_client,
                body=LockControlRequest(
                    sign=signature,
                    uuid=device_uuid,
                    action=action,
                    access_token=access_token,
                    key=FORD_APP_KEY,
                    timestamp=timestamp,
                ),
            )

            return response is not None and getattr(response, "code", 1) == 0
        finally:
            await lock_client.get_async_httpx_client().aclose()

    async def get_device_info(self, device: WyzeDevice) -> dict:
        """
        Get detailed information about a device.

        Fetches the latest device info from the API. This can be used to get
        updated device state that may not be captured in the initial device list.

        Args:
            device: The device to get information for.

        Returns:
            Dictionary containing detailed device information.
        """
        await self._ensure_token_valid()

        client = self._get_main_client()

        response = await get_device_info.asyncio(
            client=client,
            body=GetDeviceInfoBody(
                device_mac=device.mac or "",
                device_model=device.product_model or "",
                **self._common_params(),
            ),
        )

        if (
            response is None
            or isinstance(response.data, Unset)
            or response.data is None
        ):
            return {}

        return response.data.additional_properties

    async def get_device_properties(
        self, device: WyzeDevice, property_ids: Optional[list[str]] = None
    ) -> dict[str, str]:
        """
        Get property values for a device.

        Fetches the current property values from the API. Properties represent
        device state like power status, brightness, color, etc.

        Args:
            device: The device to get properties for.
            property_ids: Optional list of specific property IDs to fetch.
                         If None, fetches all properties for the device.

        Returns:
            Dictionary mapping property ID to property value.
        """
        await self._ensure_token_valid()

        client = self._get_main_client()

        request_kwargs: dict = {
            "device_mac": device.mac or "",
            "device_model": device.product_model or "",
            **self._common_params(),
        }
        if property_ids:
            request_kwargs["target_pid_list"] = property_ids

        response = await get_property_list.asyncio(
            client=client,
            body=GetPropertyListRequest(**request_kwargs),
        )

        if (
            response is None
            or isinstance(response.data, Unset)
            or response.data is None
        ):
            return {}

        if (
            isinstance(response.data.property_list, Unset)
            or response.data.property_list is None
        ):
            return {}

        result = {}
        for prop in response.data.property_list:
            if not isinstance(prop.pid, Unset) and not isinstance(prop.value, Unset):
                result[prop.pid] = prop.value
        return result

    async def get_camera_events(
        self,
        device: WyzeDevice,
        count: int = 20,
        begin_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> list[CameraEvent]:
        """
        Get recent events for a camera.

        Args:
            device: The camera device to get events for.
            count: Maximum number of events to retrieve (default 20).
            begin_time: Start timestamp in milliseconds (optional).
            end_time: End timestamp in milliseconds (optional).

        Returns:
            List of CameraEvent objects.
        """
        await self._ensure_token_valid()

        client = self._get_main_client()

        request_kwargs: dict = {
            "count": count,
            "device_mac_list": [device.mac] if device.mac else [],
            **self._common_params(),
        }
        if begin_time is not None:
            request_kwargs["begin_time"] = begin_time
        if end_time is not None:
            request_kwargs["end_time"] = end_time

        response = await get_event_list.asyncio(
            client=client,
            body=GetEventListBody(**request_kwargs),
        )

        if (
            response is None
            or isinstance(response.data, Unset)
            or response.data is None
        ):
            return []

        if (
            isinstance(response.data.event_list, Unset)
            or response.data.event_list is None
        ):
            return []

        return [
            CameraEvent.from_api_response(event.to_dict())
            for event in response.data.event_list
        ]

    async def get_plug_usage(
        self,
        device: WyzeDevice,
        start_time: int,
        end_time: int,
    ) -> list[PlugUsageRecord]:
        """
        Get power usage history for a smart plug.

        Args:
            device: The plug device to get usage for.
            start_time: Start timestamp in milliseconds.
            end_time: End timestamp in milliseconds.

        Returns:
            List of PlugUsageRecord objects with date and usage data.
        """
        await self._ensure_token_valid()

        client = self._get_main_client()

        response = await get_plug_usage_history.asyncio(
            client=client,
            body=PlugUsageRequest(
                device_mac=device.mac or "",
                date_begin=start_time,
                date_end=end_time,
                **self._common_params(),
            ),
        )

        if (
            response is None
            or isinstance(response.data, Unset)
            or response.data is None
        ):
            return []

        if (
            isinstance(response.data.usage_record_list, Unset)
            or response.data.usage_record_list is None
        ):
            return []

        return [
            PlugUsageRecord.from_api_response(record.to_dict())
            for record in response.data.usage_record_list
        ]

    async def get_lock_info(
        self,
        device: WyzeDevice,
        with_keypad: bool = False,
    ) -> LockInfo:
        """
        Get detailed information about a lock.

        Args:
            device: The lock device to get information for.
            with_keypad: Whether to include keypad information.

        Returns:
            LockInfo object with lock status and door state.
        """
        await self._ensure_token_valid()

        lock_client = Client(base_url=LOCK_API_SERVER)

        try:
            timestamp = str(int(time.time() * 1000))
            device_uuid = device.mac or ""
            access_token = self._get_token().access_token

            # Build payload for signature
            payload = {
                "access_token": access_token,
                "key": FORD_APP_KEY,
                "timestamp": timestamp,
                "uuid": device_uuid,
            }
            if with_keypad:
                payload["with_keypad"] = "1"

            signature = ford_create_signature(
                "/openapi/lock/v1/info", "GET", payload
            )

            response = await get_lock_info.asyncio(
                client=lock_client,
                uuid=device_uuid,
                access_token=access_token,
                key=FORD_APP_KEY,
                timestamp=timestamp,
                sign=signature,
            )

            if response is None:
                return LockInfo(uuid="", is_online=False, is_locked=False, door_open=False, raw={})

            raw_data = response.to_dict() if hasattr(response, "to_dict") else {}
            return LockInfo.from_api_response(raw_data)
        finally:
            await lock_client.get_async_httpx_client().aclose()

    async def get_thermostat_state(
        self,
        device: WyzeDevice,
    ) -> ThermostatState:
        """
        Get current thermostat state.

        Args:
            device: The thermostat device.

        Returns:
            ThermostatState object with current temperature, setpoints, and mode.
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = int(time.time() * 1000)

        # Keys to request - common thermostat properties
        keys = "temperature,humidity,cool_sp,heat_sp,mode_sys,fan_mode,working_state,temp_unit"
        payload = {"keys": keys, "did": device.mac or "", "nonce": str(nonce)}
        signature = olive_create_signature(payload, access_token)

        platform_client = AuthenticatedClient(
            base_url=PLATFORM_SERVICE_URL,
            token=access_token,
            prefix="",
            auth_header_name="access_token",
        )

        try:
            response = await get_thermostat_iot_prop.asyncio(
                client=platform_client,
                keys=keys,
                did=device.mac or "",
                nonce=nonce,
                appid=OLIVE_APP_ID,
                appinfo=APP_INFO,
                phoneid=self._phone_id,
                signature2=signature,
            )

            if response is None:
                return ThermostatState(
                    temperature=None,
                    humidity=None,
                    cool_setpoint=None,
                    heat_setpoint=None,
                    mode=None,
                    fan_mode=None,
                    working_state=None,
                    raw={},
                )

            raw_data = response.to_dict() if hasattr(response, "to_dict") else {}
            return ThermostatState.from_api_response(raw_data)
        finally:
            await platform_client.get_async_httpx_client().aclose()

    async def set_thermostat_properties(
        self,
        device: WyzeDevice,
        *,
        cool_setpoint: Optional[int] = None,
        heat_setpoint: Optional[int] = None,
        fan_mode: Optional[str] = None,
        hvac_mode: Optional[str] = None,
    ) -> bool:
        """
        Set thermostat properties.

        Args:
            device: The thermostat device.
            cool_setpoint: Cooling setpoint temperature.
            heat_setpoint: Heating setpoint temperature.
            fan_mode: Fan mode ('auto', 'on', 'cycle').
            hvac_mode: HVAC mode ('off', 'heat', 'cool', 'auto').

        Returns:
            True if successful, False otherwise.
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))

        # Build props
        props = SetThermostatIotPropBodyProps()
        if cool_setpoint is not None:
            props["cool_sp"] = cool_setpoint
        if heat_setpoint is not None:
            props["heat_sp"] = heat_setpoint
        if fan_mode is not None:
            props["fan_mode"] = fan_mode
        if hvac_mode is not None:
            props["mode_sys"] = hvac_mode

        body = SetThermostatIotPropBody(
            did=device.mac or "",
            model=device.product_model or "",
            props=props,
            is_sub_device=0,
            nonce=nonce,
        )

        # Create signature from body dict
        body_dict = body.to_dict()
        signature = olive_create_signature(body_dict, access_token)

        platform_client = AuthenticatedClient(
            base_url=PLATFORM_SERVICE_URL,
            token=access_token,
            prefix="",
            auth_header_name="access_token",
        )

        try:
            response = await set_thermostat_iot_prop.asyncio(
                client=platform_client,
                body=body,
                appid=OLIVE_APP_ID,
                appinfo=APP_INFO,
                phoneid=self._phone_id,
                signature2=signature,
            )

            return response is not None and getattr(response, "code", None) == "1"
        finally:
            await platform_client.get_async_httpx_client().aclose()

    async def get_irrigation_zones(
        self,
        device: WyzeDevice,
    ) -> list[IrrigationZone]:
        """
        Get irrigation zones for a controller.

        Args:
            device: The irrigation controller device.

        Returns:
            List of IrrigationZone objects.
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))
        device_id = device.mac or ""

        payload = {"device_id": device_id, "nonce": nonce}
        signature = olive_create_signature(payload, access_token)

        platform_client = AuthenticatedClient(
            base_url=PLATFORM_SERVICE_URL,
            token=access_token,
            prefix="",
            auth_header_name="access_token",
        )

        try:
            response = await get_irrigation_zones.asyncio(
                client=platform_client,
                device_id=device_id,
                nonce=nonce,
                appid=OLIVE_APP_ID,
                appinfo=APP_INFO,
                phoneid=self._phone_id,
                signature2=signature,
            )

            if response is None or isinstance(response.data, Unset):
                return []

            # Extract zones from response data
            zones_data = getattr(response.data, "zones", [])
            if isinstance(zones_data, Unset):
                zones_data = []

            return [
                IrrigationZone.from_api_response(
                    zone.to_dict() if hasattr(zone, "to_dict") else zone
                )
                for zone in zones_data
            ]
        finally:
            await platform_client.get_async_httpx_client().aclose()

    async def run_irrigation(
        self,
        device: WyzeDevice,
        zones: list[tuple[int, int]],
    ) -> bool:
        """
        Start irrigation on specified zones.

        Args:
            device: The irrigation controller device.
            zones: List of (zone_number, duration_seconds) tuples.

        Returns:
            True if successful, False otherwise.
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))
        device_id = device.mac or ""

        # Build zone runs list
        zone_runs = [
            IrrigationQuickRunRequestZoneRunsItem(zone_number=zone_num, duration=duration)
            for zone_num, duration in zones
        ]

        body = IrrigationQuickRunRequest(
            device_id=device_id,
            nonce=nonce,
            zone_runs=zone_runs,
        )

        # Create signature from body dict
        body_dict = body.to_dict()
        signature = olive_create_signature(body_dict, access_token)

        platform_client = AuthenticatedClient(
            base_url=PLATFORM_SERVICE_URL,
            token=access_token,
            prefix="",
            auth_header_name="access_token",
        )

        try:
            response = await irrigation_quick_run.asyncio(
                client=platform_client,
                body=body,
                appid=OLIVE_APP_ID,
                appinfo=APP_INFO,
                phoneid=self._phone_id,
                signature2=signature,
            )

            return response is not None and getattr(response, "code", None) == "1"
        finally:
            await platform_client.get_async_httpx_client().aclose()

    async def stop_irrigation(
        self,
        device: WyzeDevice,
    ) -> bool:
        """
        Stop all running irrigation on a controller.

        Args:
            device: The irrigation controller device.

        Returns:
            True if successful, False otherwise.
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))
        device_id = device.mac or ""

        body = IrrigationStopRequest(
            device_id=device_id,
            nonce=nonce,
            action=IrrigationStopRequestAction.STOP,
        )

        # Create signature from body dict
        body_dict = body.to_dict()
        signature = olive_create_signature(body_dict, access_token)

        platform_client = AuthenticatedClient(
            base_url=PLATFORM_SERVICE_URL,
            token=access_token,
            prefix="",
            auth_header_name="access_token",
        )

        try:
            response = await stop_irrigation_schedule.asyncio(
                client=platform_client,
                body=body,
                appid=OLIVE_APP_ID,
                appinfo=APP_INFO,
                phoneid=self._phone_id,
                signature2=signature,
            )

            return response is not None and getattr(response, "code", None) == "1"
        finally:
            await platform_client.get_async_httpx_client().aclose()

    # -------------------------------------------------------------------------
    # Camera Control Methods
    # -------------------------------------------------------------------------

    async def set_camera_motion_detection(
        self,
        device: WyzeDevice,
        enabled: bool,
    ) -> bool:
        """
        Enable or disable motion detection on a camera.

        Args:
            device: The camera device.
            enabled: True to enable, False to disable.

        Returns:
            True if successful, False otherwise.
        """
        value = "1" if enabled else "0"

        if device.product_model in DEVICEMGMT_API_MODELS:
            return await self._run_devicemgmt_action(
                device,
                DeviceMgmtRunActionRequestCapabilitiesItemName.IOT_DEVICE,
                {"motion-detect-recording": enabled},
            )
        else:
            # For older cameras, set both properties
            result1 = await self.set_property(device, PropertyID.MOTION_DETECTION, value)
            result2 = await self.set_property(device, PropertyID.MOTION_DETECTION_TOGGLE, value)
            return result1 and result2

    async def set_camera_floodlight(
        self,
        device: WyzeDevice,
        enabled: bool,
    ) -> bool:
        """
        Turn camera floodlight on or off.

        Args:
            device: The camera device (must have floodlight capability).
            enabled: True to turn on, False to turn off.

        Returns:
            True if successful, False otherwise.
        """
        if device.product_model == "AN_RSCW":
            # Battery Cam Pro uses spotlight
            return await self._run_devicemgmt_action(
                device,
                DeviceMgmtRunActionRequestCapabilitiesItemName.SPOTLIGHT,
                {"on": enabled},
            )
        elif device.product_model in DEVICEMGMT_API_MODELS:
            # Floodlight Pro and other devicemgmt cameras
            return await self._run_devicemgmt_action(
                device,
                DeviceMgmtRunActionRequestCapabilitiesItemName.FLOODLIGHT,
                {"on": enabled},
            )
        else:
            # Older cameras use ACCESSORY property
            # "1" = on, "2" = off (not "0"!)
            value = "1" if enabled else "2"
            return await self.set_property(device, PropertyID.ACCESSORY, value)

    async def _run_devicemgmt_action(
        self,
        device: WyzeDevice,
        capability_name: DeviceMgmtRunActionRequestCapabilitiesItemName,
        properties: dict,
    ) -> bool:
        """
        Run a device management action on a newer camera model.

        Args:
            device: The camera device.
            capability_name: The capability to control (floodlight, spotlight, siren, iot-device).
            properties: Dictionary of property name to value.

        Returns:
            True if successful, False otherwise.
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = int(time.time() * 1000)

        # Build properties list
        props_list = [
            DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem(
                prop=prop_name, value=str(prop_value)
            )
            for prop_name, prop_value in properties.items()
        ]

        body = DeviceMgmtRunActionRequest(
            capabilities=[
                DeviceMgmtRunActionRequestCapabilitiesItem(
                    name=capability_name,
                    properties=props_list,
                )
            ],
            nonce=nonce,
            target_info=DeviceMgmtRunActionRequestTargetInfo(
                id=device.mac or "",
                type_=DeviceMgmtRunActionRequestTargetInfoType.DEVICE,
            ),
        )

        # Create signature from body dict
        body_dict = body.to_dict()
        signature = olive_create_signature(body_dict, access_token)

        devicemgmt_client = AuthenticatedClient(
            base_url=DEVICEMGMT_SERVICE_URL,
            token=access_token,
            prefix="",
            auth_header_name="access_token",
        )

        try:
            response = await device_mgmt_run_action.asyncio(
                client=devicemgmt_client,
                body=body,
            )

            return response is not None and getattr(response, "code", None) == "1"
        finally:
            await devicemgmt_client.get_async_httpx_client().aclose()
