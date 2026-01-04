"""
Wyzeapy - A Python wrapper for the Wyze API.

This module provides a high-level async interface for interacting with Wyze smart home devices.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Awaitable, Callable, List, Optional, Union

from .models.device import create_device, WyzeDevice

from .wyze_api_client import Client
from .wyze_api_client.api.authentication import login_with_credentials, login_with_2fa
from .wyze_api_client.api.devices import get_object_list
from .wyze_api_client.models import (
    LoginRequest,
    TwoFactorLoginRequest,
    TwoFactorLoginRequestMfaType,
    CommonRequestParams,
    Device,
)


# API Server URLs
AUTH_SERVER = "https://auth-prod.api.wyze.com"
MAIN_API_SERVER = "https://api.wyzecam.com"

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


def _hash_password(password: str) -> str:
    """Triple MD5 hash the password as required by Wyze API."""
    for _ in range(3):
        password = hashlib.md5(password.encode()).hexdigest()
    return password


class Wyzeapy:
    """
    High-level async interface for the Wyze API.

    Example:
        ```python
        async with Wyzeapy("email@example.com", "password", key_id, api_key) as wyze:
            devices = await wyze.list_devices()
            for device in devices:
                print(f"{device.nickname}: {device.product_model}")
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
        self._password_hash = _hash_password(password)
        self._key_id = key_id
        self._api_key = api_key
        self._phone_id = str(uuid.uuid4())
        self._tfa_callback = tfa_callback

        self._token: Optional[Token] = None
        self._auth_client: Optional[Client] = None
        self._main_client: Optional[Client] = None

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
            raise RuntimeError(f"Login failed: {result.status_code} - {result.content.decode()}")

        response = result.parsed
        if response is None:
            raise RuntimeError(f"Login failed: could not parse response - {result.content.decode()}")

        # Check for 2FA requirement
        if response.mfa_options is not None:
            if "TotpVerificationCode" in response.mfa_options:
                return await self._handle_2fa("TOTP", response.mfa_details.totp_apps[0].app_id)

            if "PrimaryPhone" in response.mfa_options:
                return await self._handle_2fa("SMS", response.sms_session_id)

        if response.access_token is None:
            raise RuntimeError(f"Login failed: {getattr(response, 'error_code', 'unknown error')}")

        self._token = Token(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
        )
        return self._token

    async def _handle_2fa(self, auth_type: str, verification_id: str) -> Token:
        """Handle two-factor authentication."""
        if self._tfa_callback is None:
            raise RuntimeError(
                f"Two-factor authentication ({auth_type}) required but no tfa_callback provided"
            )

        # Call the callback (may be sync or async)
        code = self._tfa_callback(auth_type)
        if hasattr(code, "__await__"):
            code = await code

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

        if response is None or response.access_token is None:
            raise RuntimeError("2FA login failed")

        self._token = Token(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
        )
        return self._token

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
            "access_token": self._token.access_token if self._token else "",
        }

    async def list_devices(self) -> List[WyzeDevice]:
        """
        Get all devices associated with the account.

        Returns:
            List of Device objects
        """
        if self._token is None:
            raise RuntimeError("Not authenticated")

        client = self._get_main_client()

        response = await get_object_list.asyncio(
            client=client,
            body=CommonRequestParams(**self._common_params()),
        )

        if response is None or response.data is None:
            return []

        return [create_device(device) for device in response.data.device_list or []]
