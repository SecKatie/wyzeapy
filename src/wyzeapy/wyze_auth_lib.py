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

from wyzeapy.const import API_KEY, PHONE_ID, APP_NAME, APP_VERSION, SC, SV, PHONE_SYSTEM_TYPE, APP_VER
from wyzeapy.exceptions import UnknownApiError, AccessTokenError
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
            self.token = await self.get_token_with_username_password(self._username, self._password)

        return self

    async def close(self):
        await self._session.close()

    async def get_token_with_username_password(self, username, password) -> Token:
        login_payload = {
            "email": username,
            "password": create_password(password)
        }

        headers = {
            "X-API-Key": API_KEY
        }

        response_json = await self.post("https://auth-prod.api.wyze.com/user/login", headers=headers,
                                        json=login_payload)

        if response_json.get('errorCode') is not None:
            _LOGGER.error(f"Unable to login with response from Wyze: {response_json}")
            raise UnknownApiError(response_json)

        return Token(response_json['access_token'], response_json['refresh_token'], time.time())

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
