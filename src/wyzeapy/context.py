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
        """Get the current access token."""
        return self.get_token().access_token

    def nonce(self) -> str:
        """Generate a nonce for API requests."""
        return str(int(time.time() * 1000))
