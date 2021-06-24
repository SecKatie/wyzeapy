#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import datetime
import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, Optional, List, Coroutine

import aiohttp
import asyncio
from aiohttp import ClientSession, TCPConnector

from .const import (
    API_KEY,
    APP_VERSION,
    PHONE_SYSTEM_TYPE,
    APP_VER,
    PHONE_ID,
    APP_NAME,
    OLIVE_APP_ID,
    APP_INFO
)
from .crypto import olive_create_signature
from .exceptions import (
    ParameterError,
    AccessTokenError,
    UnknownApiError,
    ActionNotSupported
)
from .payload_factory import (
    ford_create_payload,
    olive_create_get_payload,
    olive_create_post_payload,
    olive_create_hms_payload,
    olive_create_hms_patch_payload,
    olive_create_hms_get_payload
)
from .types import ResponseCodes, Device, DeviceTypes, ThermostatProps, Group

_LOGGER = logging.getLogger(__name__)


class NetClient:
    access_token = ""
    refresh_token = ""
    _session: ClientSession
    _conn: TCPConnector
    _hms_id: Optional[str]

    def __init__(self):
        self._hms_id = None

    async def async_init(self):
        self._conn = aiohttp.TCPConnector(ttl_dns_cache=(30 * 60))  # Set DNS cache to 30 minutes
        self._session = aiohttp.ClientSession(connector=self._conn)

    async def async_close(self):
        await self._session.close()

    async def login(self, email: str, password: str) -> bool:
        login_payload = {
            "email": email,
            "password": self.create_password(password)
        }

        headers = {
            "X-API-Key": API_KEY
        }

        async with self._session.post("https://auth-prod.api.wyze.com/user/login", headers=headers,
                                      json=login_payload) as response:
            response_json: Dict[Any, Any] = await response.json()

            if response_json.get('errorCode') is not None:
                _LOGGER.error(f"Unable to login with response from Wyze: {response_json}")
                return False

            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']

            return True

    async def can_login(self, username: str, password: str) -> bool:
        return await self.login(username, password)

    @staticmethod
    def create_password(password: str) -> str:
        hex1 = hashlib.md5(password.encode()).hexdigest()
        hex2 = hashlib.md5(hex1.encode()).hexdigest()
        return hashlib.md5(hex2.encode()).hexdigest()

    @staticmethod
    def check_for_errors(response_json: Dict[str, Any]) -> None:
        if response_json['code'] != ResponseCodes.SUCCESS.value:
            if response_json['code'] == ResponseCodes.PARAMETER_ERROR.value:
                raise ParameterError(response_json)
            elif response_json['code'] == ResponseCodes.ACCESS_TOKEN_ERROR.value:
                raise AccessTokenError
            else:
                raise UnknownApiError(response_json)

    @staticmethod
    def check_for_errors_lock(response_json: Dict[str, Any]) -> None:
        if response_json['ErrNo'] != ResponseCodes.SUCCESS.value:
            if response_json['code'] == ResponseCodes.PARAMETER_ERROR.value:
                raise ParameterError
            elif response_json['code'] == ResponseCodes.ACCESS_TOKEN_ERROR.value:
                raise AccessTokenError
            else:
                raise UnknownApiError(response_json)

    async def get_object_list(self) -> Dict[Any, Any]:
        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        async with self._session.post("https://api.wyzecam.com/app/v2/home_page/get_object_list",
                                      json=payload) as response:
            response_json: Dict[Any, Any] = await response.json()

            self.check_for_errors(response_json)

            return response_json

    async def get_property_list(self, device: Device) -> Dict[Any, Any]:
        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "device_model": device.product_model,
            "device_mac": device.mac,
            "target_pid_list": []
        }

        async with self._session.post("https://api.wyzecam.com/app/v2/device/get_property_list",
                                      json=payload) as response:
            response_json = await response.json()

            self.check_for_errors(response_json)

            return response_json

    async def get_auto_group_list(self) -> Dict[Any, Any]:
        payload = {
            "access_token": self.access_token,
            "app_name": APP_NAME,
            "app_ver": APP_VER,
            "app_version": APP_VERSION,
            "group_type": "0",
            "phone_id": PHONE_ID,
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "ts": int(time.time()),
        }

        async with self._session.post("https://api.wyzecam.com/app/v2/auto_group/get_list",
                                      json=payload) as response:
            response_json = await response.json()

            self.check_for_errors(response_json)

            return response_json

    async def get_device_info(self, device: Device) -> Dict[Any, Any]:
        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "device_mac": device.mac,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "device_model": device.product_model,
            "sv": "c86fa16fc99d4d6580f82ef3b942e586",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        async with self._session.post("https://api.wyzecam.com/app/v2/device/get_device_Info",
                                      json=payload) as response:
            response_json = await response.json()

            self.check_for_errors(response_json)

            return response_json

    async def run_action_list(self, device: Device, plist: List[Dict[Any, Any]]) -> None:

        if DeviceTypes(device.product_type) not in [
            DeviceTypes.MESH_LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "action_list": [
                {
                    "instance_id": device.mac,
                    "action_params": {
                        "list": [
                            {
                                "mac": device.mac,
                                "plist": plist
                            }
                        ]
                    },
                    "provider_key": device.product_model,
                    "action_key": "set_mesh_property"
                }
            ]
        }

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post("https://api.wyzecam.com/app/v2/auto/run_action_list",
                                            json=payload)))

    async def auto_group_run(self, group: Group) -> None:
        payload = {
            "access_token": self.access_token,
            "app_name": APP_NAME,
            "app_ver": APP_VER,
            "app_version": APP_VERSION,
            "group_id": group.group_id,
            "phone_id": PHONE_ID,
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "ts": int(time.time()),
        }

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post("https://api.wyzecam.com/app/v2/auto_group/run",
                                            json=payload)))

    async def run_action(self, device: Device, action: str) -> None:

        if DeviceTypes(device.product_type) not in [
            DeviceTypes.CAMERA
        ]:
            raise ActionNotSupported(device.product_type)

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "provider_key": device.product_model,
            "instance_id": device.mac,
            "action_key": action,
            "action_params": {},
            "custom_string": "",
        }

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post("https://api.wyzecam.com/app/v2/auto/run_action",
                                            json=payload)))

    async def set_property_list(self, device: Device, plist: List[Dict[str, str]]) -> None:

        if DeviceTypes(device.product_type) not in [
            DeviceTypes.LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "property_list": plist,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post("https://api.wyzecam.com/app/v2/device/set_property_list",
                                            json=payload)))

    async def set_property(self, device: Device, pid: str, pvalue: str) -> None:

        """
        Sets a single property on the selected device.
        Only works for Plugs, Lights, and Outdoor Plugs

        :param device: Device
        :param pid: str
        :param pvalue: str
        :return: None
        """
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.PLUG,
            DeviceTypes.LIGHT,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            raise ActionNotSupported(device.product_type)

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "pvalue": pvalue,
            "pid": pid,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post("https://api.wyzecam.com/app/v2/device/set_property",
                                            json=payload)))

    async def get_full_event_list(self, count: int) -> Dict[Any, Any]:
        payload = {
            "phone_id": PHONE_ID,
            "begin_time": int((time.time() - (60 * 60)) * 1000),
            "event_type": "",
            "app_name": APP_NAME,
            "count": count,
            "app_version": APP_VERSION,
            "order_by": 2,
            "event_value_list": [
                "1",
                "13",
                "10",
                "12"
            ],
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "device_mac_list": [],
            "event_tag_list": [],
            "sv": "782ced6909a44d92a1f70d582bbe88be",
            "end_time": int(time.time() * 1000),
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_ver": APP_VER,
            "ts": 1623612037763,
            "device_mac": "",
            "access_token": self.access_token
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.wyzecam.com/app/v2/device/get_event_list",
                                          json=payload) as response:
                return await response.json()

    async def get_event_list(self, device: Device, count: int) -> Dict[str, Any]:

        """
        Gets motion events from the event listing endpoint.

        :param count:
        :param device: Device
        :return: dict
        """
        payload = {
            "phone_id": PHONE_ID,
            "begin_time": int(str(datetime.date.today().strftime("%s")) + "000"),
            "event_type": "",
            "app_name": APP_NAME,
            "count": count,
            "app_version": APP_VERSION,
            "order_by": 2,
            "event_value_list": [
                "1",
                "13",
                "10",
                "12"
            ],
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "device_mac_list": [
                device.mac
            ],
            "event_tag_list": [],
            "sv": "782ced6909a44d92a1f70d582bbe88be",
            "end_time": int(str(int(time.time())) + "000"),
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_ver": APP_VER,
            "ts": int(str(int(time.time())) + "000"),
            "device_mac": "",
            "access_token": self.access_token
        }

        async with self._session.post("https://api.wyzecam.com/app/v2/device/get_event_list",
                                      json=payload) as response:
            response_json = await response.json()

            self.check_for_errors(response_json)

            return response_json

    async def lock_control(self, device: Device, action: str) -> None:
        url_path = "/openapi/lock/v1/control"

        device_uuid = device.mac.split(".")[2]

        payload = {
            "uuid": device_uuid,
            "action": action  # "remoteLock" or "remoteUnlock"
        }
        payload = ford_create_payload(self.access_token, payload, url_path, "post")

        url = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/control"

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post(url, json=payload)))

    async def thermostat_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        payload = olive_create_get_payload(device.mac)
        signature = olive_create_signature(payload, self.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self.access_token,
            'signature2': signature
        }

        url = 'https://wyze-earth-service.wyzecam.com/plugin/earth/get_iot_prop'

        async with self._session.get(url, headers=headers, params=payload) as response:
            response_json: Dict[Any, Any] = await response.json()

            self.check_for_errors_thermostat(response_json)

            return response_json

    async def thermostat_set_iot_prop(self, device: Device, prop: ThermostatProps, value: Any) -> None:
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic"
        payload = olive_create_post_payload(device.mac, device.product_model, prop, value)
        signature = olive_create_signature(json.dumps(payload, separators=(',', ':')), self.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self.access_token,
            'signature2': signature
        }

        payload_str = json.dumps(payload, separators=(',', ':'))

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.post(url, headers=headers, data=payload_str)))

    @staticmethod
    def check_for_errors_thermostat(response_json: Dict[Any, Any]) -> None:
        if response_json['code'] != 1:
            raise UnknownApiError(response_json)

    async def get_plan_binding_list_by_user(self) -> Dict[Any, Any]:
        url = "https://wyze-membership-service.wyzecam.com/platform/v2/membership/get_plan_binding_list_by_user"
        payload = olive_create_hms_payload()
        signature = olive_create_signature(payload, self.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self.access_token,
            'signature2': signature
        }

        async with self._session.get(url, headers=headers, params=payload) as response:
            return await response.json()

    async def get_hms_id(self) -> Optional[str]:
        if self._hms_id is not None:
            return self._hms_id

        response = await self.get_plan_binding_list_by_user()
        hms_subs = response['data']

        if len(hms_subs) >= 1:
            for sub in hms_subs:
                if (devices := sub.get('deviceList')) is not None and len(devices) >= 1:
                    for device in devices:
                        self._hms_id = str(device['device_id'])
                        return self._hms_id

        return None

    async def monitoring_profile_active(self, hms_id: str, home: int, away: int) -> Dict[Any, Any]:
        url = "https://hms.api.wyze.com/api/v1/monitoring/v1/profile/active"
        query = olive_create_hms_patch_payload(hms_id)
        signature = olive_create_signature(query, self.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self.access_token,
            'signature2': signature,
            'Authorization': self.access_token
        }
        payload = [
            {
                "state": "home",
                "active": home
            },
            {
                "state": "away",
                "active": away
            }
        ]

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.patch(url, headers=headers, params=query, json=payload)))

    async def disable_reme_alarm(self, hms_id: str) -> None:
        url = "https://hms.api.wyze.com/api/v1/reme-alarm"
        payload = {
            "hms_id": hms_id,
            "remediation_id": "emergency"
        }
        headers = {
            "Authorization": self.access_token
        }

        loop = asyncio.get_event_loop()
        loop.create_task(self.send_request(self._session.delete(url, headers=headers, json=payload)))

    async def monitoring_profile_state_status(self, hms_id: str) -> Dict[Any, Any]:
        url = "https://hms.api.wyze.com/api/v1/monitoring/v1/profile/state-status"
        query = olive_create_hms_get_payload(hms_id)
        signature = olive_create_signature(query, self.access_token)
        headers = {
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self.access_token,
            'signature2': signature,
            'Authorization': self.access_token,
            'Content-Type': "application/json"
        }

        async with self._session.get(url, headers=headers, params=query) as response:
            response_json = await response.json()
            return response_json

    async def send_request(self, request):
        async with request as response:
            if os.getenv("DEBUG"):
                print(f"Request response: {await response.json()}")
            pass