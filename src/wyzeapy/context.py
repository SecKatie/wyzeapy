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
    :param create_platform_client: Function to create platform API client.
    :type create_platform_client: Callable[[], AuthenticatedClient]
    :param create_app_client: Function to create app API client.
    :type create_app_client: Callable[[], AuthenticatedClient]
    :param create_lock_client: Function to create lock API client.
    :type create_lock_client: Callable[[], Client]
    :param create_devicemgmt_client: Function to create device management API client.
    :type create_devicemgmt_client: Callable[[], AuthenticatedClient]
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
    create_platform_client: Callable[[], AuthenticatedClient]
    create_app_client: Callable[[], AuthenticatedClient]
    create_lock_client: Callable[[], Client]
    create_devicemgmt_client: Callable[[], AuthenticatedClient]

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

    def nonce(self) -> str:
        """
        Generate a nonce for API requests.

        :returns: Nonce string (timestamp in milliseconds).
        :rtype: str
        """
        return str(int(time.time() * 1000))
