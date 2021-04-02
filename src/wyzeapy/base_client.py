#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy

import hashlib
import time
import uuid
from enum import Enum

import requests

PHONE_SYSTEM_TYPE = "1"
API_KEY = 'WMXHYf79Nr5gIlt3r0r7p9Tcw5bvs6BB4U8O8nGJ'
APP_VERSION = "2.18.43"
APP_VER = "com.hualai.WyzeCam___2.18.43"
APP_NAME = "com.hualai.WyzeCam"
PHONE_ID = str(uuid.uuid4())


class DeviceTypes(Enum):
    LIGHT = "Light"
    PLUG = "Plug"
    OUTDOOR_PLUG = "OutdoorPlug"
    MESH_LIGHT = "MeshLight"
    CAMERA = "Camera"
    CHIME_SENSOR = "ChimeSensor"


class PropertyIDs(Enum):
    ON = "P3"
    AVAILABLE = "P5"
    BRIGHTNESS = "P1501"  # From 0-100
    COLOR_TEMP = "P1502"  # In Kelvin
    COLOR = "P1507"  # As a hex string RrGgBb


class ResponseCodes(Enum):
    SUCCESS = "1"
    PARAMETER_ERROR = "1001"
    ACCESS_TOKEN_ERROR = "2001"


SWITCHABLE_DEVICES = [DeviceTypes.LIGHT, DeviceTypes.MESH_LIGHT, DeviceTypes.PLUG]


class ActionNotSupported(Exception):
    def __init__(self, device_type):
        message = "The action specified is not supported by device type: {}".format(device_type)

        super().__init__(message)


class ParameterError(Exception):
    pass


class AccessTokenError(Exception):
    pass


class UnknownApiError(Exception):
    def __init__(self, response_json):
        super(UnknownApiError, self).__init__(str(response_json))


class Device:
    product_type: str
    product_model: str
    mac: str
    nickname: str

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<Device: {}, {}>".format(DeviceTypes(self.product_type), self.mac)


class BaseClient:
    access_token = ""
    refresh_token = ""

    def login(self, email, password) -> None:
        email = email
        password = password

        login_payload = {
            "email": email,
            "password": self.create_password(password)
        }

        headers = {
            "X-API-Key": API_KEY
        }

        response_json = requests.post("https://auth-prod.api.wyze.com/user/login",
                                      headers=headers, json=login_payload).json()

        self.access_token = response_json['access_token']
        self.refresh_token = response_json['refresh_token']

    @staticmethod
    def create_password(password) -> str:
        hex1 = hashlib.md5(password.encode()).hexdigest()
        hex2 = hashlib.md5(hex1.encode()).hexdigest()
        return hashlib.md5(hex2.encode()).hexdigest()

    @staticmethod
    def check_for_errors(response_json):
        if response_json['code'] != ResponseCodes.SUCCESS.value:
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

        response_json = requests.post("https://api.wyzecam.com/app/v2/home_page/get_object_list",
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
            "device_list": [device.mac],
            "target_pid_list": ["P3", "P5", "P1501", "P1502", "P1506", "P1507", "P1509", "P1511", "P1512"]
        }

        response_json = requests.post("https://api.wyzecam.com/app/v2/device_list/get_property_list",
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

        response_json = requests.post("https://api.wyzecam.com/app/v2/auto/run_action_list", json=payload).json()

        self.check_for_errors(response_json)

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
        response_json = requests.post("https://api.wyzecam.com/app/v2/device/set_property_list", json=payload).json()

        self.check_for_errors(response_json)

    def set_property(self, device: Device, pid, pvalue):
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
        response_json = requests.post("https://api.wyzecam.com/app/v2/device/set_property", json=payload).json()

        self.check_for_errors(response_json)
