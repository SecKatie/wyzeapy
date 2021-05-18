#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import datetime
import hashlib
import json
import logging
import time
from typing import Any

import requests
import cachecontrol
from cachecontrol import CacheControl

from .const import *
from .payload_factory import ford_create_payload, olive_create_get_payload, olive_create_post_payload
from .crypto import olive_create_signature
from .exceptions import *
from .types import ResponseCodes, Device, DeviceTypes, ThermostatProps, Group

_LOGGER = logging.getLogger(__name__)

class BaseClient:
    access_token = ""
    refresh_token = ""

    def __init__(self):
        self._session: CacheControl = cachecontrol.CacheControl(requests.Session())

    def __del__(self):
        self._session.close()

    def login(self, email, password) -> bool:
        email = email
        password = password

        login_payload = {
            "email": email,
            "password": self.create_password(password)
        }

        headers = {
            "X-API-Key": API_KEY
        }

        response_json: dict = self._session.post("https://auth-prod.api.wyze.com/user/login",
                                      headers=headers, json=login_payload).json()

        if response_json.get('errorCode') is not None:
            _LOGGER.error(f"Unable to login with response from Wyze: {response_json}")
            return False

        self.access_token = response_json['access_token']
        self.refresh_token = response_json['refresh_token']

        return True

    def can_login(self, username, password):
        return self.login(username, password)

    @staticmethod
    def create_password(password) -> str:
        hex1 = hashlib.md5(password.encode()).hexdigest()
        hex2 = hashlib.md5(hex1.encode()).hexdigest()
        return hashlib.md5(hex2.encode()).hexdigest()

    @staticmethod
    def check_for_errors(response_json):
        if response_json['code'] != ResponseCodes.SUCCESS.value:
            if response_json['code'] == ResponseCodes.PARAMETER_ERROR.value:
                raise ParameterError(response_json)
            elif response_json['code'] == ResponseCodes.ACCESS_TOKEN_ERROR.value:
                raise AccessTokenError
            else:
                raise UnknownApiError(response_json)

    @staticmethod
    def check_for_errors_lock(response_json):
        if response_json['ErrNo'] != ResponseCodes.SUCCESS.value:
            if response_json['code'] == ResponseCodes.PARAMETER_ERROR.value:
                raise ParameterError
            elif response_json['code'] == ResponseCodes.ACCESS_TOKEN_ERROR.value:
                raise AccessTokenError
            else:
                raise UnknownApiError(response_json)

    def get_object_list(self):
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/home_page/get_object_list",
                                      json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def get_property_list(self, device: Device):
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/device/get_property_list",
                                      json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def get_auto_group_list(self):
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/auto_group/get_list",
                                      json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def run_action_list(self, device: Device, plist):
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/auto/run_action_list", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def auto_group_run(self, group: Group):
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/auto_group/run", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def run_action(self, device: Device, action: str):
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/auto/run_action", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def set_property_list(self, device: Device, plist):
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
        response_json = self._session.post("https://api.wyzecam.com/app/v2/device/set_property_list", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def set_property(self, device: Device, pid, pvalue):
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
        response_json = self._session.post("https://api.wyzecam.com/app/v2/device/set_property", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def get_event_list(self, device: Device, count: int) -> dict:
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

        response_json = self._session.post("https://api.wyzecam.com/app/v2/device/get_event_list", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def lock_control(self, device: Device, action: str):
        url_path = "/openapi/lock/v1/control"

        device_uuid = device.mac.split(".")[2]

        payload = {
            "uuid": device_uuid,
            "action": action  # "remoteLock" or "remoteUnlock"
        }
        payload = ford_create_payload(self.access_token, payload, url_path, "post")

        url = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/control"

        response_json = self._session.post(url, json=payload).json()

        return response_json

    def thermostat_get_iot_prop(self, device: Device):
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
        response_json = self._session.get(url, headers=headers, params=payload).json()

        self.check_for_errors_thermostat(response_json)

        return response_json

    def thermostat_set_iot_prop(self, device: Device, prop: ThermostatProps, value: Any):
        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic"
        payload = olive_create_post_payload(device.mac, device.product_model, prop, value)
        signature = olive_create_signature(json.dumps(payload, separators=(',', ':')), self.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self.access_token,
            'signature2': signature
        }

        self._session.headers.update(headers)

        req = self._session.prepare_request(requests.Request('POST', url, json=payload))

        payload = json.dumps(payload, separators=(',', ':'))

        req.body = payload.encode('utf-8')
        req.prepare_content_length(req.body)

        response_json = self._session.send(req).json()

        self.check_for_errors_thermostat(response_json)

        return response_json

    @staticmethod
    def check_for_errors_thermostat(response_json):
        if response_json['code'] != 1:
            raise UnknownApiError(response_json)
