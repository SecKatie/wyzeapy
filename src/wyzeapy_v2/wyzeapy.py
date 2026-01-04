"""
Wyzeapy - A Python wrapper for the Wyze API.

This module provides a high-level async interface for interacting with Wyze smart home devices.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional, Union

from .wyze_api_client.api.user import get_user_profile

from .devices import create_device, WyzeDevice
from .exceptions import (
    AuthenticationError,
    TwoFactorAuthRequired,
    TokenRefreshError,
    NotAuthenticatedError,
)
from .utils import (
    hash_password,
    ford_create_signature,
    olive_create_signature,
    PropertyID,
    FORD_APP_KEY,
    OLIVE_APP_ID,
    APP_INFO,
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
from .wyze_api_client.api.lock import lock_control
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
)
from .wyze_api_client.types import Unset


# API Server URLs
AUTH_SERVER = "https://auth-prod.api.wyze.com"
MAIN_API_SERVER = "https://api.wyzecam.com"
LOCK_API_SERVER = "https://yd-saas-toc.wyzecam.com"

# App constants
PHONE_SYSTEM_TYPE = "1"
APP_VERSION = "2.18.43"
APP_VER = "com.hualai.WyzeCam___2.18.43"
APP_NAME = "com.hualai.WyzeCam"
SC = "9f275790cab94a72bd206c8876429f3c"
SV = "9d74946e652647e9b6c9d59326aef104"

# Type alias for 2FA callback: receives auth_type ("TOTP" or "SMS"), returns verification code
TwoFactorCallback = Callable[[str], Union[str, Awaitable[str]]]


@dataclass
class Token:
    """Represents Wyze API access and refresh tokens."""

    access_token: str
    refresh_token: str
    created_at: float = field(default_factory=time.time)

    REFRESH_INTERVAL = 82800  # 23 hours

    @property
    def should_refresh(self) -> bool:
        return time.time() >= (self.created_at + self.REFRESH_INTERVAL)


@dataclass
class WyzeUser:
    """Represents a Wyze user profile."""

    notifications_enabled: bool = False

    # Identity
    user_id: Optional[str] = None

    # Profile fields
    nickname: Optional[str] = None
    logo_url: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[str] = None
    occupation: Optional[str] = None

    # Body metrics (for Wyze Scale integration)
    height: Optional[float] = None
    height_unit: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    body_type: Optional[str] = None

    # Account info
    create_time: Optional[int] = None  # Timestamp in milliseconds
    update_time: Optional[int] = None  # Timestamp in milliseconds
    subscription: Optional[dict] = None
    metadata: Optional[dict] = None
    is_voip_on: Optional[bool] = None

    # Raw data for any unmodeled fields
    raw_data: dict = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict) -> "WyzeUser":
        """Create WyzeUser from API response data."""
        return cls(
            notifications_enabled=data.get("notification", False),
            user_id=data.get("user_id"),
            nickname=data.get("nickname"),
            logo_url=data.get("logo_url"),
            gender=data.get("gender"),
            birthdate=data.get("birthdate"),
            occupation=data.get("occupation"),
            height=data.get("height"),
            height_unit=data.get("height_unit"),
            weight=data.get("weight"),
            weight_unit=data.get("weight_unit"),
            body_type=data.get("body_type"),
            create_time=data.get("create_time"),
            update_time=data.get("update_time"),
            subscription=data.get("subscription"),
            metadata=data.get("metadata"),
            is_voip_on=data.get("is_voip_on"),
            raw_data=data,
        )


# Platform service URL
PLATFORM_SERVICE_URL = "https://wyze-platform-service.wyzecam.com"


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
