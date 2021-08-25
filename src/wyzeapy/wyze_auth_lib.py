#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import time
from typing import Dict, Any, Optional

import aiohttp
from aiohttp import TCPConnector, ClientSession

from wyzeapy.const import API_KEY, PHONE_ID, APP_NAME, APP_VERSION, SC, SV, PHONE_SYSTEM_TYPE, APP_VER, APP_INFO
from wyzeapy.exceptions import UnknownApiError, AccessTokenError, TwoFactorAuthenticationEnabled
from wyzeapy.utils import create_password, check_for_errors_standard

_LOGGER = logging.getLogger(__name__)


class Token:
    def __init__(self, access_token, refresh_token, last_login_time):
        self.access_token: str = access_token
        self.refresh_token: str = refresh_token
        self.last_login_time: float = last_login_time


class WyzeAuthLib:
    token: Optional[Token] = None
    _conn: TCPConnector
    _session: ClientSession

    def __init__(self, username=None, password=None, token: Token = None):
        self._username = username
        self._password = password
        self.token = token
        self.session_id = ""
        self.verification_id = ""
        self.two_factor_type = None

    async def gen_session(self):
        self._conn = aiohttp.TCPConnector(ttl_dns_cache=(30 * 60))  # Set DNS cache to 30 minutes
        self._session = aiohttp.ClientSession(connector=self._conn)

    @classmethod
    async def create(cls, username=None, password=None, token: Token = None):
        self = cls(username=username, password=password, token=token)

        await self.gen_session()

        if self._username is None and self._password is None and self.token is None:
            raise AttributeError("Must provide a username, password or token")
        elif self.token is None and self._username is not None and self._password is not None:
            assert self._username != ""
            assert self._password != ""

        return self

    async def close(self):
        await self._session.close()

    async def get_token_with_username_password(self, username, password) -> Token:
        self._username = username
        self._password = create_password(password)
        login_payload = {
            "email": self._username,
            "password": self._password
        }

        headers = {
            'Phone-Id': PHONE_ID,
            'User-Agent': APP_INFO,
            'X-API-Key': API_KEY,
        }

        response_json = await self.post("https://auth-prod.api.wyze.com/user/login", headers=headers,
                                        json=login_payload)

        if response_json.get('errorCode') is not None:
            _LOGGER.error(f"Unable to login with response from Wyze: {response_json}")
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

        self.token = Token(response_json['access_token'], response_json['refresh_token'], time.time())
        return self.token

    async def get_token_with_2fa(self, verification_code) -> Token:
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

        self.token = Token(response_json['access_token'], response_json['refresh_token'], time.time(), True)
        return self.token

    @property
    def should_refresh(self) -> bool:
        return time.time() - self.token.last_login_time > 59 * 60 * 60

    async def refresh_if_should(self):
        if self.should_refresh:
            _LOGGER.debug("Should refresh. Refreshing...")
            try:
                await self.refresh()
            except AccessTokenError:
                _LOGGER.warning("Could not refresh. Logging in with the Username and Password...")
                self.token = await self.get_token_with_username_password(self._username, self._password)

    async def refresh(self) -> None:
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

        response = await self._session.post("https://api.wyzecam.com/app/user/refresh_token", headers=headers,
                                            json=payload)
        response_json = await response.json()
        check_for_errors_standard(response_json)

        self.token.access_token = response_json['data']['access_token']
        self.token.refresh_token = response_json['data']['refresh_token']

    async def post(self, url, json=None, headers=None, data=None) -> Dict[Any, Any]:
        _LOGGER.debug("Request:")
        _LOGGER.debug(f"url: {url}")
        _LOGGER.debug(f"json: {json}")
        _LOGGER.debug(f"headers: {headers}")
        _LOGGER.debug(f"data: {data}")

        response = await self._session.post(url, json=json, headers=headers, data=data)
        return await response.json()

    async def get(self, url, headers=None, params=None) -> Dict[Any, Any]:
        response = await self._session.get(url, params=params, headers=headers)
        return await response.json()

    async def patch(self, url, headers=None, params=None, json=None) -> Dict[Any, Any]:
        response = await self._session.patch(url, headers=headers, params=params, json=json)
        return await response.json()

    async def delete(self, url, headers=None, json=None) -> Dict[Any, Any]:
        response = await self._session.delete(url, headers=headers, json=json)
        return await response.json()
