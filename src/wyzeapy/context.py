"""API context for device classes."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Token
    from .wyze_api_client import Client, AuthenticatedClient


@dataclass
class WyzeApiContext:
    """
    Context providing API access for device classes.

    This is a lightweight object that provides device classes with everything
    they need to make API calls, without exposing the full Wyzeapy instance.

    :param phone_id: Phone ID for API authentication.
    :type phone_id: str
    :param get_token: Function to get current token.
    :type get_token: Callable[[], Token]
    :param ensure_token_valid: Async function to refresh token if needed.
    :type ensure_token_valid: Callable[[], Awaitable[None]]
    :param get_main_client: Function to get main API client.
    :type get_main_client: Callable[[], Client]
    :param get_platform_client: Function to get platform API client.
    :type get_platform_client: Callable[[], AuthenticatedClient]
    :param get_app_client: Function to get app API client.
    :type get_app_client: Callable[[], AuthenticatedClient]
    :param get_lock_client: Function to get lock API client.
    :type get_lock_client: Callable[[], Client]
    :param get_devicemgmt_client: Function to get device management API client.
    :type get_devicemgmt_client: Callable[[], AuthenticatedClient]
    :param olive_create_signature: Function to create olive API signatures.
    :type olive_create_signature: Callable[[dict[str, Any] | str, str], str]
    :param ford_create_signature: Function to create lock API signatures.
    :type ford_create_signature: Callable[[str, str, dict[str, Any]], str]
    :param build_common_params: Function to build common API parameters.
    :type build_common_params: Callable[[], dict[str, Any]]
    """

    # Core identity
    phone_id: str

    # Token access (getter, not value - to ensure fresh token)
    get_token: Callable[[], Token]
    ensure_token_valid: Callable[[], Awaitable[None]]

    # HTTP client access
    get_main_client: Callable[[], Client]
    get_platform_client: Callable[[], AuthenticatedClient]
    get_app_client: Callable[[], AuthenticatedClient]
    get_lock_client: Callable[[], Client]
    get_devicemgmt_client: Callable[[], AuthenticatedClient]

    # Signature utilities
    olive_create_signature: Callable[[dict[str, Any] | str, str], str]
    ford_create_signature: Callable[[str, str, dict[str, Any]], str]

    # Common params builder
    build_common_params: Callable[[], dict[str, Any]]

    @property
    def access_token(self) -> str:
        """
        Get the current access token.

        :returns: Current access token.
        :rtype: str
        """
        return self.get_token().access_token

    async def get_access_token(self) -> str:
        """
        Ensure token is valid and return access token.

        :returns: Current access token.
        :rtype: str
        """
        await self.ensure_token_valid()
        return self.get_token().access_token

    def nonce(self) -> str:
        """
        Generate a nonce for API requests.

        :returns: Nonce string (timestamp in milliseconds).
        :rtype: str
        """
        return str(int(time.time() * 1000))

    async def main_client(self) -> Client:
        """Get the main API client with token validation."""
        await self.ensure_token_valid()
        return self.get_main_client()

    async def platform_client(self) -> AuthenticatedClient:
        """Get the platform API client with token validation."""
        await self.ensure_token_valid()
        return self.get_platform_client()

    async def app_client(self) -> AuthenticatedClient:
        """Get the app API client with token validation."""
        await self.ensure_token_valid()
        return self.get_app_client()

    async def lock_client(self) -> Client:
        """Get the lock API client with token validation."""
        await self.ensure_token_valid()
        return self.get_lock_client()

    async def devicemgmt_client(self) -> AuthenticatedClient:
        """Get the device management API client with token validation."""
        await self.ensure_token_valid()
        return self.get_devicemgmt_client()
