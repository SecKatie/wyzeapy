#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import asyncio
import logging
import time
from typing import Dict, Any, Optional

from aiohttp import TCPConnector, ClientSession, ContentTypeError

from .const import API_KEY, PHONE_ID, APP_NAME, APP_VERSION, SC, SV, PHONE_SYSTEM_TYPE, APP_VER, APP_INFO
from .exceptions import (
    UnknownApiError,
    TwoFactorAuthenticationEnabled,
    AccessTokenError,
)
from .utils import create_password, check_for_errors_standard

_LOGGER = logging.getLogger(__name__)
"""
Authentication token data and timing management.

This module handles Wyze API authentication tokens, including expiration
tracking, automatic refresh timing, and secure request methods in WyzeAuthLib.
"""

class Token:
    """Represents Wyze API access/refresh token and expiration tracking.

    Attributes:
        _access_token: Current access token string.
        _refresh_token: Current refresh token string.
        expired: Flag indicating if the token is marked expired.
        _refresh_time: Unix timestamp when token should be refreshed.

    Class Attributes:
        REFRESH_INTERVAL: Time in seconds before token auto-refresh (23h).
    """
    # Token is good for 24 hours; schedule refresh after 23 hours
    REFRESH_INTERVAL = 82800

    def __init__(self, access_token, refresh_token, refresh_time: float = None):
        self._access_token: str = access_token
        self._refresh_token: str = refresh_token
        self.expired = False
        if refresh_time:
            self._refresh_time: float = refresh_time
        else:
            self._refresh_time: float = time.time() + Token.REFRESH_INTERVAL

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token
        self._refresh_time = time.time() + Token.REFRESH_INTERVAL

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        self._refresh_token = refresh_token

    @property
    def refresh_time(self):
        return self._refresh_time


class WyzeAuthLib:
    token: Optional[Token] = None
    SANITIZE_FIELDS = [
        "email",
        "password",
        "access_token",
        "accessToken",
        "refresh_token",
        "lat",
        "lon",
        "address",
    ]
    SANITIZE_STRING = "**Sanitized**"

    def __init__(
        self,
        username=None,
        password=None,
        key_id=None,
        api_key=None,
        token: Optional[Token] = None,
        token_callback=None,
    ):
        """Initialize WyzeAuthLib for authentication and token management.

        Args:
            username: Wyze account email address.
            password: Plaintext or hashed account password.
            key_id: Third-party API key ID for Wyze credentials.
            api_key: Third-party API key for Wyze credentials.
            token: Existing Token instance for reuse (optional).
            token_callback: Callback to invoke on token updates.
        """
        self._username = username
        self._password = password
        self._key_id = key_id
        self._api_key = api_key
        self.token = token
        self.session_id = ""
        self.verification_id = ""
        self.two_factor_type = None
        self.refresh_lock = asyncio.Lock()
        self.token_callback = token_callback

    @classmethod
    async def create(
        cls,
        username=None,
        password=None,
        key_id=None,
        api_key=None,
        token: Optional[Token] = None,
        token_callback=None,
    ):
        """Factory to instantiate WyzeAuthLib with credentials or existing token.

        Args:
            username: Wyze account email (optional if token provided).
            password: Wyze account password (optional if token provided).
            key_id: Third-party API key ID (required for login).
            api_key: Third-party API key (required for login).
            token: Existing Token instance (skip login flow).
            token_callback: Callback for token refresh events.

        Returns:
            A configured WyzeAuthLib instance.

        Raises:
            AttributeError: When neither credentials nor token are provided.
        """
        self = cls(
            username=username,
            password=password,
            key_id=key_id,
            api_key=api_key,
            token=token,
            token_callback=token_callback,
        )

        if self._username is None and self._password is None and self.token is None:
            raise AttributeError("Must provide a username, password or token")
        elif self.token is None and self._username is not None and self._password is not None:
            assert self._username != ""
            assert self._password != ""

        return self

    async def get_token_with_username_password(
        self, username, password, key_id, api_key
    ) -> Token:
        """Authenticate using email/password and retrieve new Token.

        Args:
            username: Wyze account email.
            password: Plaintext Wyze account password.
            key_id: Third-party API key ID.
            api_key: Third-party API key.

        Returns:
            A new Token instance with access and refresh tokens.

        Raises:
            TwoFactorAuthenticationEnabled: When 2FA is required.
            AccessTokenError: On invalid credentials.
            UnknownApiError: For other authentication errors.
        """
        self._username = username
        self._password = create_password(password)
        self._key_id = key_id
        self._api_key = api_key
        login_payload = {"email": self._username, "password": self._password}

        headers = {
            "keyid": key_id,
            "apikey": api_key,
            "User-Agent": "wyzeapy",
        }

        response_json = await self.post(
            "https://auth-prod.api.wyze.com/api/user/login",
            headers=headers,
            json=login_payload,
        )

        if response_json.get('errorCode') is not None:
            _LOGGER.error(f"Unable to login with response from Wyze: {response_json}")
            if response_json["errorCode"] == 1000:
                raise AccessTokenError
            raise UnknownApiError(response_json)

        if response_json.get('mfa_options') is not None:
            # Store the TOTP verification setting in the token and raise exception
            if "TotpVerificationCode" in response_json.get("mfa_options"):
                self.two_factor_type = "TOTP"
                # Store the verification_id from the response, it's needed for the 2fa payload.
                self.verification_id = response_json["mfa_details"]["totp_apps"][0]["app_id"]
                raise TwoFactorAuthenticationEnabled
                # 2fa using SMS, store sms as 2fa method in token, send the code then raise exception
            if "PrimaryPhone" in response_json.get("mfa_options"):
                self.two_factor_type = "SMS"
                params = {
                    'mfaPhoneType': 'Primary',
                    'sessionId': response_json.get("sms_session_id"),
                    'userId': response_json['user_id'],
                }
                response_json = await self.post('https://auth-prod.api.wyze.com/user/login/sendSmsCode',
                                                headers=headers, data=params)
                # Store the session_id from this response, it's needed for the 2fa payload.
                self.session_id = response_json['session_id']
                raise TwoFactorAuthenticationEnabled

        self.token = Token(response_json['access_token'], response_json['refresh_token'])
        await self.token_callback(self.token)
        return self.token

    async def get_token_with_2fa(self, verification_code) -> Token:
        """Complete login flow using two-factor authentication code.

        Args:
            verification_code: 6-digit TOTP or SMS code for 2FA.

        Returns:
            A new Token instance after successful 2FA verification.
        """
        headers = {
            'Phone-Id': PHONE_ID,
            'User-Agent': APP_INFO,
            'X-API-Key': API_KEY,
        }
        # TOTP Payload
        if self.two_factor_type == "TOTP":
            payload = {
                "email": self._username,
                "password": self._password,
                "mfa_type": "TotpVerificationCode",
                "verification_id": self.verification_id,
                "verification_code": verification_code
            }
        # SMS Payload
        else:
            payload = {
                "email": self._username,
                "password": self._password,
                "mfa_type": "PrimaryPhone",
                "verification_id": self.session_id,
                "verification_code": verification_code
            }

        response_json = await self.post(
            'https://auth-prod.api.wyze.com/user/login',
            headers=headers, json=payload)

        self.token = Token(response_json['access_token'], response_json['refresh_token'])
        await self.token_callback(self.token)
        return self.token

    @property
    def should_refresh(self) -> bool:
        """Check whether the current token has reached its refresh time."""
        return time.time() >= self.token.refresh_time

    async def refresh_if_should(self):
        """Refresh the token proactively if expired or past refresh_time."""
        if self.should_refresh or self.token.expired:
            async with self.refresh_lock:
                if self.should_refresh or self.token.expired:
                    _LOGGER.debug("Should refresh. Refreshing...")
                    await self.refresh()

    async def refresh(self) -> None:
        """Exchange the refresh token for a new access token and update internal Token.

        Raises:
            AccessTokenError: If refresh fails due to invalid refresh token.
            UnknownApiError: For other errors during refresh.
        """
        payload = {
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "sc": SC,
            "sv": SV,
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_ver": APP_VER,
            "ts": int(time.time()),
            "refresh_token": self.token.refresh_token
        }

        headers = {
            "X-API-Key": API_KEY
        }

        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.post("https://api.wyzecam.com/app/user/refresh_token", headers=headers,
                                           json=payload)
        response_json = await response.json()
        check_for_errors_standard(self, response_json)

        self.token.access_token = response_json['data']['access_token']
        self.token.refresh_token = response_json['data']['refresh_token']
        await self.token_callback(self.token)
        self.token.expired = False

    def sanitize(self, data):
        """Recursively sanitize sensitive fields in dicts for safe logging.

        Args:
            data: The dict to sanitize; returned sanitized copy.
        """
        if data and type(data) is dict:
            # value is unused, but it prevents us from having to split the tuple to check against SANITIZE_FIELDS
            for key, value in data.items():
                if type(value) is dict:
                    data[key] = self.sanitize(value)
                if key in self.SANITIZE_FIELDS:
                    data[key] = self.SANITIZE_STRING
        return data

    async def post(self, url, json=None, headers=None, data=None) -> Dict[Any, Any]:
        """Send an HTTP POST request with sanitized logging.

        Args:
            url: Request URL.
            json: Optional JSON payload.
            headers: Optional headers.
            data: Optional form data.

        Returns:
            Parsed JSON response.
        """
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.post(url, json=json, headers=headers, data=data)
            # Relocated these below as the sanitization seems to modify the data before it goes to the post.
            _LOGGER.debug("Request:")
            _LOGGER.debug(f"url: {url}")
            _LOGGER.debug(f"json: {self.sanitize(json)}")
            _LOGGER.debug(f"headers: {self.sanitize(headers)}")
            _LOGGER.debug(f"data: {self.sanitize(data)}")
            # Log the response.json() if it exists, if not log the response.
            try:
                response_json = await response.json()
                _LOGGER.debug(f"Response Json: {self.sanitize(response_json)}")
            except ContentTypeError:
                _LOGGER.debug(f"Response: {response}")
            return await response.json()
    
    async def put(self, url, json=None, headers=None, data=None) -> Dict[Any, Any]:
        """Send an HTTP PUT request with sanitized logging.

        See `post` for parameter details.
        """
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.put(url, json=json, headers=headers, data=data)
            # Relocated these below as the sanitization seems to modify the data before it goes to the post.
            _LOGGER.debug("Request:")
            _LOGGER.debug(f"url: {url}")
            _LOGGER.debug(f"json: {self.sanitize(json)}")
            _LOGGER.debug(f"headers: {self.sanitize(headers)}")
            _LOGGER.debug(f"data: {self.sanitize(data)}")
            # Log the response.json() if it exists, if not log the response.
            try:
                response_json = await response.json()
                _LOGGER.debug(f"Response Json: {self.sanitize(response_json)}")
            except ContentTypeError:
                _LOGGER.debug(f"Response: {response}")
            return await response.json()

    async def get(self, url, headers=None, params=None) -> Dict[Any, Any]:
        """Send an HTTP GET request with sanitized logging.

        Args:
            url: Request URL.
            headers: Optional headers.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.get(url, params=params, headers=headers)
            # Relocated these below as the sanitization seems to modify the data before it goes to the post.
            _LOGGER.debug("Request:")
            _LOGGER.debug(f"url: {url}")
            _LOGGER.debug(f"headers: {self.sanitize(headers)}")
            _LOGGER.debug(f"params: {self.sanitize(params)}")
            # Log the response.json() if it exists, if not log the response.
            try:
                response_json = await response.json()
                _LOGGER.debug(f"Response Json: {self.sanitize(response_json)}")
            except ContentTypeError:
                _LOGGER.debug(f"Response: {response}")
            return await response.json()

    async def patch(self, url, headers=None, params=None, json=None) -> Dict[Any, Any]:
        """Send an HTTP PATCH request with sanitized logging.

        See `get`/`post` for parameter details.
        """
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.patch(url, headers=headers, params=params, json=json)
            # Relocated these below as the sanitization seems to modify the data before it goes to the post.
            _LOGGER.debug("Request:")
            _LOGGER.debug(f"url: {url}")
            _LOGGER.debug(f"json: {self.sanitize(json)}")
            _LOGGER.debug(f"headers: {self.sanitize(headers)}")
            _LOGGER.debug(f"params: {self.sanitize(params)}")
            # Log the response.json() if it exists, if not log the response.
            try:
                response_json = await response.json()
                _LOGGER.debug(f"Response Json: {self.sanitize(response_json)}")
            except ContentTypeError:
                _LOGGER.debug(f"Response: {response}")
            return await response.json()

    async def delete(self, url, headers=None, json=None) -> Dict[Any, Any]:
        """Send an HTTP DELETE request with sanitized logging.

        Args:
            url: Request URL.
            headers: Optional headers.
            json: Optional JSON payload.

        Returns:
            Parsed JSON response.
        """
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.delete(url, headers=headers, json=json)
            # Relocated these below as the sanitization seems to modify the data before it goes to the post.
            _LOGGER.debug("Request:")
            _LOGGER.debug(f"url: {url}")
            _LOGGER.debug(f"json: {self.sanitize(json)}")
            _LOGGER.debug(f"headers: {self.sanitize(headers)}")
            # Log the response.json() if it exists, if not log the response.
            try:
                response_json = await response.json()
                _LOGGER.debug(f"Response Json: {self.sanitize(response_json)}")
            except ContentTypeError:
                _LOGGER.debug(f"Response: {response}")
            return await response.json()
