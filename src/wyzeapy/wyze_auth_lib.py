#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import asyncio
import logging
import time
from json import dumps
from typing import Dict, Any, Optional

from aiohttp import TCPConnector, ClientSession, ContentTypeError
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

from .const import API_KEY, PHONE_ID
from .exceptions import UnknownApiError, TwoFactorAuthenticationEnabled
from .utils import create_password, check_for_errors_standard

_LOGGER = logging.getLogger(__name__)


class Token:
    # Token is good for 216,000 seconds (60 hours) but 48 hours seems like a reasonable refresh interval
    REFRESH_INTERVAL = 172800

    def __init__(self, access_token, refresh_token, refresh_time: float = None):
        self._access_token: str = access_token
        self._refresh_token: str = refresh_token
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

    def __str__(self):
        return f"<Token (access_token='{self.access_token}', " \
               f"refresh_token='{self.refresh_token}', " \
               f"refresh_time={self.refresh_time})>"


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

    _refresh_token_sc = "9f275790cab94a72bd206c8876429f3c"
    _refresh_token_sv = "9d74946e652647e9b6c9d59326aef104"
    phone_system_type = "1"
    app_name = "com.hualai.WyzeCam"
    app_version = "2.18.43"
    app_ver = "com.hualai.WyzeCam___2.18.43"
    app_info = "wyze_android_2.19.14"  # Required for the thermostat

    def __init__(self, username=None, password=None, token: Token = None, token_callback=None):
        self._username = username
        self._password = password
        self.token = token
        self.session_id = ""
        self.verification_id = ""
        self.two_factor_type = None
        self.refresh_lock = asyncio.Lock()
        self.token_callback = token_callback

    @classmethod
    async def create(cls, username=None, password=None, token: Token = None, token_callback=None):
        self = cls(username=username, password=password, token=token, token_callback=token_callback)

        if self._username is None and self._password is None and self.token is None:
            raise AttributeError("Must provide a username, password or token")
        elif self.token is None and self._username is not None and self._password is not None:
            assert self._username != ""
            assert self._password != ""

        return self

    async def get_token_with_username_password(self, username, password) -> Token:
        self._username = username
        self._password = create_password(password)
        login_payload = {
            "email": self._username,
            "password": self._password
        }

        headers = {
            'Phone-Id': PHONE_ID,
            'User-Agent': self.app_info,
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

        self.token = Token(response_json['access_token'], response_json['refresh_token'])
        await self.token_callback(self.token)
        return self.token

    async def get_token_with_2fa(self, verification_code) -> Token:
        headers = {
            'Phone-Id': PHONE_ID,
            'User-Agent': self.app_info,
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
        return time.time() >= self.token.refresh_time

    async def refresh_if_should(self):
        if self.should_refresh:
            async with self.refresh_lock:
                if self.should_refresh:
                    _LOGGER.debug("Should refresh. Refreshing...")
                    await self.refresh()

    async def refresh(self) -> None:
        payload = {
            "phone_id": PHONE_ID,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "sc": self._refresh_token_sc,
            "sv": self._refresh_token_sv,
            "phone_system_type": self.phone_system_type,
            "app_ver": self.app_ver,
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
        check_for_errors_standard(response_json)

        self.token.access_token = response_json['data']['access_token']
        self.token.refresh_token = response_json['data']['refresh_token']
        await self.token_callback(self.token)

    def sanitize(self, data):
        if data and type(data) is dict:
            # value is unused, but it prevents us from having to split the tuple to check against SANITIZE_FIELDS
            for key, value in data.items():
                if type(value) is dict:
                    data[key] = self.sanitize(value)
                if key in self.SANITIZE_FIELDS:
                    data[key] = self.SANITIZE_STRING
        return data

    async def post(self, url, json=None, headers=None, data=None) -> Dict[Any, Any]:
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

    async def get(self, url, headers=None, params=None) -> Dict[Any, Any]:
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


class RokuAuthLib(WyzeAuthLib):
    # Captured from Android app traffic
    phone_system_type = 2
    app_name = "com.roku.rokuhome"
    app_version = "1.1.0.99"
    app_ver = "com.roku.rokuhome___1.1.0.99"
    app_info = "Owl_android/1.1.0.99"

    _aws_region = "us-east-1"
    _aws_id_pool = f"{_aws_region}:11747937-25e8-402f-8e72-6873a618692c"
    _login_host = "prod.mobile.roku.com"
    _login_uri = f"https://{_login_host}/iot/user/login"

    def __init__(self, username=None, password=None, token: Token = None, token_callback=None):
        super().__init__(username, password, token, token_callback)

        # Get an AWS identity as described at
        # https://docs.aws.amazon.com/cognito/latest/developerguide/getting-credentials.html
        self.cognito_client = boto3.client("cognito-identity", region_name=self._aws_region)
        self.cognito_id = self.cognito_client.get_id(IdentityPoolId=self._aws_id_pool)["IdentityId"]

    async def get_token_with_username_password(self, username, password) -> Token:
        self._username = username
        self._password = password
        login_payload = dumps({
            "email": self._username,
            "password": self._password
        }, separators=(",", ":")).encode("utf-8")

        # Get AWS credentials using our identity
        credentials = self.cognito_client.get_credentials_for_identity(
            IdentityId=self.cognito_id
        )["Credentials"]

        # Create a Credentials object from the response JSON
        credentials = Credentials(
            credentials["AccessKeyId"],
            credentials["SecretKey"],
            credentials["SessionToken"]
        ).get_frozen_credentials()

        # Set request headers (based on the "Roku Smart Home" Android app)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": self._login_host,
            "apiweb-env": "prod",
            "app": "harold",  # without this, the response is: "Error: Something went wrong 'emailVerified'"
        }

        # Sign request
        request = AWSRequest("POST", self._login_uri, headers, login_payload)
        signer = SigV4Auth(credentials, "execute-api", self._aws_region)
        signer.add_auth(request)

        # Send request
        response_json = await self.post(self._login_uri, headers=request.headers, data=login_payload)

        if "message" in response_json:
            _LOGGER.error(f"Unable to login with response from Roku: {response_json}")
            raise UnknownApiError(response_json)

        self.token = Token(
            response_json["data"]["partnerAccess"]["token"],
            response_json["data"]["oauth"]["refreshToken"]
        )

        await self.token_callback(self.token)
        return self.token
