"""
Wyzeapy - A Python wrapper for the Wyze API.

This module provides a high-level async interface for interacting with Wyze smart home devices.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from .wyze_api_client.api.user import get_user_profile

from .models import (
    Token,
    WyzeUser,
    HomeFavorites,
)
from .services.hms import WyzeHMS
from .context import WyzeApiContext
from .exceptions import (
    AuthenticationError,
    TwoFactorAuthRequired,
    TokenRefreshError,
    NotAuthenticatedError,
    ApiRequestError,
)

if TYPE_CHECKING:
    from .devices import (
        WyzeDevice,
        WyzeCamera,
        WyzeLight,
        WyzeLock,
        WyzePlug,
        WyzeThermostat,
        WyzeSensor,
    )
from .utils import hash_password, ford_create_signature, olive_create_signature
from .const import (
    AUTH_SERVER,
    MAIN_API_SERVER,
    APP_API_SERVER,
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
    OLIVE_APP_ID,
)

from .wyze_api_client import Client, AuthenticatedClient
from .wyze_api_client.api.authentication import (
    login_with_credentials,
    login_with_2fa,
    refresh_token,
)
from .wyze_api_client.api.devices import get_object_list
from .wyze_api_client.api.home import get_home_favorites
from .wyze_api_client.models import (
    LoginRequest,
    TwoFactorLoginRequest,
    TwoFactorLoginRequestMfaType,
    CommonRequestParams,
    RefreshTokenRequest,
    GetHomeFavoritesRequest,
)
from .wyze_api_client.types import Unset


# Type alias for 2FA callback: receives auth_type ("TOTP" or "SMS"), returns verification code
TwoFactorCallback = Callable[[str], str | Awaitable[str]]


class Wyzeapy:
    """
    High-level async interface for the Wyze API.

    Example::

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

    With 2FA::

        def get_2fa_code(auth_type: str) -> str:
            return input(f"Enter {auth_type} code: ")

        async with Wyzeapy(email, password, key_id, api_key, tfa_callback=get_2fa_code) as wyze:
            devices = await wyze.list_devices()
    """

    def __init__(
        self,
        email: str,
        password: str,
        key_id: str,
        api_key: str,
        tfa_callback: TwoFactorCallback | None = None,
    ):
        self._email: str = email
        self._password_hash: str = hash_password(password)
        self._key_id: str = key_id
        self._api_key: str = api_key
        self._phone_id: str = str(uuid.uuid4())
        self._tfa_callback: TwoFactorCallback | None = tfa_callback

        self._token: Token | None = None
        self._token_refresh_lock: asyncio.Lock = asyncio.Lock()
        self._auth_client: Client | None = None
        self._main_client: Client | None = None
        self._platform_client: AuthenticatedClient | None = None
        self._app_client: AuthenticatedClient | None = None
        self._lock_client: Client | None = None
        self._devicemgmt_client: AuthenticatedClient | None = None
        self._hms: WyzeHMS | None = None

    @property
    def phone_id(self) -> str:
        """Get the phone ID used for API authentication."""
        return self._phone_id

    @classmethod
    async def create(
        cls,
        email: str,
        password: str,
        key_id: str,
        api_key: str,
        tfa_callback: TwoFactorCallback | None = None,
    ) -> "Wyzeapy":
        """
        Create and authenticate a Wyzeapy client.

        This is a convenience method that creates a client and logs in.
        Note: You should call ``close()`` when done, or use the async context manager instead.

        :param email: Wyze account email.
        :type email: str
        :param password: Wyze account password.
        :type password: str
        :param key_id: Wyze API key ID.
        :type key_id: str
        :param api_key: Wyze API key.
        :type api_key: str
        :param tfa_callback: Optional callback for 2FA authentication.
        :type tfa_callback: TwoFactorCallback | None
        :returns: Authenticated Wyzeapy client instance.
        :rtype: Wyzeapy

        Example::

            wyze = await Wyzeapy.create(email, password, key_id, api_key)
            try:
                devices = await wyze.list_devices()
            finally:
                await wyze.close()
        """
        client = cls(email, password, key_id, api_key, tfa_callback)
        _ = await client._login()
        return client

    async def close(self) -> None:
        """Close HTTP clients and clean up resources."""
        clients: list[Client | AuthenticatedClient | None] = [
            self._auth_client,
            self._main_client,
            self._platform_client,
            self._app_client,
            self._lock_client,
            self._devicemgmt_client,
        ]
        for client in clients:
            if client is not None:
                await client.get_async_httpx_client().aclose()
        self._auth_client = None
        self._main_client = None
        self._platform_client = None
        self._app_client = None
        self._lock_client = None
        self._devicemgmt_client = None

    async def __aenter__(self) -> "Wyzeapy":
        """Login and return self."""
        _ = await self._login()
        return self

    async def __aexit__(self, *args) -> None:
        """Clean up HTTP clients."""
        await self.close()

    def _get_auth_client(self) -> Client:
        if self._auth_client is None:
            self._auth_client = Client(base_url=AUTH_SERVER)
        return self._auth_client

    def _get_main_client(self) -> Client:
        if self._main_client is None:
            self._main_client = Client(base_url=MAIN_API_SERVER)
        return self._main_client

    def _get_platform_client(self) -> AuthenticatedClient:
        """Get persistent authenticated client for platform service API."""
        if self._platform_client is None:
            self._platform_client = AuthenticatedClient(
                base_url=PLATFORM_SERVICE_URL,
                token=self._get_token().access_token,
                prefix="",
                auth_header_name="access_token",
            )
        return self._platform_client

    def _get_app_client(self) -> AuthenticatedClient:
        """Get persistent authenticated client for app API."""
        if self._app_client is None:
            self._app_client = AuthenticatedClient(
                base_url=APP_API_SERVER,
                token=self._get_token().access_token,
                prefix="",
                auth_header_name="Access_token",
            )
        return self._app_client

    def _get_lock_client(self) -> Client:
        """Get persistent client for lock API."""
        if self._lock_client is None:
            self._lock_client = Client(base_url=LOCK_API_SERVER)
        return self._lock_client

    def _get_devicemgmt_client(self) -> AuthenticatedClient:
        """Get persistent authenticated client for device management API."""
        if self._devicemgmt_client is None:
            self._devicemgmt_client = AuthenticatedClient(
                base_url=DEVICEMGMT_SERVICE_URL,
                token=self._get_token().access_token,
                prefix="",
                auth_header_name="access_token",
            )
        return self._devicemgmt_client

    def get_context(self) -> WyzeApiContext:
        """
        Get API context for device classes.

        Returns a lightweight context object that provides device classes
        with everything they need to make API calls.

        :returns: WyzeApiContext object for device API access.
        :rtype: WyzeApiContext
        """
        return WyzeApiContext(
            phone_id=self._phone_id,
            get_token=self._get_token,
            ensure_token_valid=self._ensure_token_valid,
            get_main_client=self._get_main_client,
            get_platform_client=self._get_platform_client,
            get_app_client=self._get_app_client,
            get_lock_client=self._get_lock_client,
            get_devicemgmt_client=self._get_devicemgmt_client,
            olive_create_signature=olive_create_signature,
            ford_create_signature=ford_create_signature,
            build_common_params=self._common_params,
        )

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
        if not isinstance(response.mfa_options, Unset):
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
                if not isinstance(response.sms_session_id, Unset):
                    return await self._handle_2fa("SMS", response.sms_session_id)
                raise AuthenticationError("SMS 2FA required but no session ID provided")

        if isinstance(response.access_token, Unset):
            raise AuthenticationError(
                f"Login failed: {getattr(response, 'error_code', 'unknown error')}"
            )

        if isinstance(response.refresh_token, Unset):
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

        if isinstance(response.access_token, Unset):
            raise AuthenticationError("2FA login failed: no access token")

        if isinstance(response.refresh_token, Unset):
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

        if isinstance(response.data, Unset):
            raise TokenRefreshError("Token refresh failed: no data in response")

        if isinstance(response.data.access_token, Unset):
            raise TokenRefreshError("Token refresh failed: no access token")

        if isinstance(response.data.refresh_token, Unset):
            raise TokenRefreshError("Token refresh failed: no refresh token")

        self._token = Token(
            access_token=response.data.access_token,
            refresh_token=response.data.refresh_token,
        )

        # Invalidate clients that have stale token baked into headers
        await self._invalidate_authenticated_clients()

        return self._token

    async def _invalidate_authenticated_clients(self) -> None:
        """Close and reset authenticated clients that have stale tokens."""
        if self._platform_client is not None:
            await self._platform_client.get_async_httpx_client().aclose()
            self._platform_client = None
        if self._app_client is not None:
            await self._app_client.get_async_httpx_client().aclose()
            self._app_client = None
        if self._devicemgmt_client is not None:
            await self._devicemgmt_client.get_async_httpx_client().aclose()
            self._devicemgmt_client = None

    async def _ensure_token_valid(self) -> None:
        """Check if token needs refresh and refresh if necessary."""
        if self._token is None:
            raise NotAuthenticatedError("Not authenticated")

        if self._token.should_refresh:
            async with self._token_refresh_lock:
                # Double-check after acquiring lock (another task may have refreshed)
                if self._token.should_refresh:
                    await self._refresh_token()

    def _common_params(self) -> dict[str, Any]:
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
    def hms(self) -> WyzeHMS:
        """
        Access the Home Monitoring Service (HMS) API.

        :returns: WyzeHMS instance for HMS operations.
        :rtype: WyzeHMS

        Example::

            async with Wyzeapy(email, password, key_id, api_key) as wyze:
                status = await wyze.hms.get_status("your-hms-id")
                await wyze.hms.set_mode("your-hms-id", HMSMode.AWAY)
        """
        if self._hms is None:
            self._hms = WyzeHMS(self)
        return self._hms

    async def list_devices(
        self, device_type: type[WyzeDevice] | None = None
    ) -> list[WyzeDevice]:
        """
        Get devices associated with the account, optionally filtered by type.

        :param device_type: Optional device class to filter by (e.g., WyzeLight, WyzeLock).
        :type device_type: type[WyzeDevice] | None
        :returns: List of Device objects with control methods available.
        :rtype: list[WyzeDevice]

        Example::

            # Get all devices
            devices = await wyze.list_devices()

            # Get only lights
            lights = await wyze.list_devices(WyzeLight)

            # Get only locks
            locks = await wyze.list_devices(WyzeLock)
        """
        from .devices import create_device

        await self._ensure_token_valid()

        client = self._get_main_client()

        response = await get_object_list.asyncio(
            client=client,
            body=CommonRequestParams(**self._common_params()),
        )

        if response is None:
            raise ApiRequestError("list_devices")

        if isinstance(response.data, Unset):
            return []

        devices = [
            create_device(device, self) for device in response.data.device_list or []
        ]

        if device_type is not None:
            devices = [d for d in devices if isinstance(d, device_type)]

        return devices

    async def get_cameras(self) -> list[WyzeCamera]:
        """
        Get all camera devices.

        :returns: List of WyzeCamera objects.
        :rtype: list[WyzeCamera]
        """
        from .devices import WyzeCamera

        devices = await self.list_devices(WyzeCamera)
        return [d for d in devices if isinstance(d, WyzeCamera)]

    async def get_lights(self) -> list[WyzeLight]:
        """
        Get all light devices (bulbs, light strips, mesh lights).

        :returns: List of WyzeLight objects.
        :rtype: list[WyzeLight]
        """
        from .devices import WyzeLight

        devices = await self.list_devices(WyzeLight)
        return [d for d in devices if isinstance(d, WyzeLight)]

    async def get_locks(self) -> list[WyzeLock]:
        """
        Get all lock devices.

        :returns: List of WyzeLock objects.
        :rtype: list[WyzeLock]
        """
        from .devices import WyzeLock

        devices = await self.list_devices(WyzeLock)
        return [d for d in devices if isinstance(d, WyzeLock)]

    async def get_plugs(self) -> list[WyzePlug]:
        """
        Get all plug devices.

        :returns: List of WyzePlug objects.
        :rtype: list[WyzePlug]
        """
        from .devices import WyzePlug

        devices = await self.list_devices(WyzePlug)
        return [d for d in devices if isinstance(d, WyzePlug)]

    async def get_thermostats(self) -> list[WyzeThermostat]:
        """
        Get all thermostat devices.

        :returns: List of WyzeThermostat objects.
        :rtype: list[WyzeThermostat]
        """
        from .devices import WyzeThermostat

        devices = await self.list_devices(WyzeThermostat)
        return [d for d in devices if isinstance(d, WyzeThermostat)]

    async def get_sensors(self) -> list[WyzeSensor]:
        """
        Get all sensor devices (contact, motion, leak sensors).

        :returns: List of WyzeSensor objects.
        :rtype: list[WyzeSensor]
        """
        from .devices import WyzeSensor

        devices = await self.list_devices(WyzeSensor)
        return [d for d in devices if isinstance(d, WyzeSensor)]

    async def get_user(self) -> WyzeUser:
        """
        Get the current user's profile.

        :returns: WyzeUser object with profile information
        :rtype: WyzeUser
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))
        payload = {"nonce": nonce}
        signature = olive_create_signature(payload, access_token)

        platform_client = self._get_platform_client()

        response = await get_user_profile.asyncio(
            client=platform_client,
            nonce=nonce,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=self._phone_id,
            signature2=signature,
        )

        if response is None:
            raise ApiRequestError("get_user")

        if isinstance(response.data, Unset):
            return WyzeUser()

        data_dict = response.data.to_dict()
        return WyzeUser.from_response(data_dict)

    async def get_home_favorites(self, home_id: str) -> HomeFavorites:
        """
        Get favorites and device list for a home.

        This endpoint returns all devices in the home with their favorite status,
        device category, and other metadata.

        :param home_id: The home ID to get favorites for.
        :type home_id: str
        :returns: HomeFavorites object containing the device list and home info.
        :rtype: HomeFavorites

        Example::

            async with Wyzeapy(email, password, key_id, api_key) as wyze:
                favorites = await wyze.get_home_favorites("your-home-id")
                for device in favorites.devices:
                    print(f"{device.nickname}: {device.device_category}")
                # Get only favorited devices
                for fav in favorites.favorite_devices:
                    print(f"Favorite: {fav.nickname}")
        """
        await self._ensure_token_valid()

        access_token = self._get_token().access_token
        nonce = str(int(time.time() * 1000))

        body = GetHomeFavoritesRequest(
            home_id=home_id,
            nonce=nonce,
        )

        body_dict = body.to_dict()
        signature = olive_create_signature(body_dict, access_token)

        app_client = self._get_app_client()

        response = await get_home_favorites.asyncio(
            client=app_client,
            body=body,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=self._phone_id,
            signature2=signature,
        )

        if response is None:
            raise ApiRequestError("get_home_favorites", f"home_id={home_id}")

        if isinstance(response.data, Unset):
            return HomeFavorites(home_id="", home_name="", devices=[], raw={})

        data_dict = response.data.to_dict()
        return HomeFavorites.from_api_response(data_dict)
