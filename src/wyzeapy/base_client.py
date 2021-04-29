#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import datetime
import hashlib
import time
import uuid
from enum import Enum
from typing import List, Dict

import requests

PHONE_SYSTEM_TYPE = "1"
API_KEY = "WMXHYf79Nr5gIlt3r0r7p9Tcw5bvs6BB4U8O8nGJ"
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
    CONTACT_SENSOR = "ContactSensor"
    MOTION_SENSOR = "MotionSensor"
    WRIST = "Wrist"
    BASE_STATION = "BaseStation"
    SCALE = "WyzeScale"
    LOCK = "Lock"
    GATEWAY = "gateway"
    COMMON = "Common"
    VACUUM = "JA_RO2"
    HEADPHONES = "JA.SC"
    THERMOSTAT = "Thermostat"
    GATEWAY_V2 = "GateWay"


class PropertyIDs(Enum):
    ON = "P3"
    AVAILABLE = "P5"
    BRIGHTNESS = "P1501"  # From 0-100
    COLOR_TEMP = "P1502"  # In Kelvin
    COLOR = "P1507"  # As a hex string RrGgBb
    DOOR_OPEN = "P2001"  # 0 if the door is closed


class ResponseCodes(Enum):
    SUCCESS = "1"
    PARAMETER_ERROR = "1001"
    ACCESS_TOKEN_ERROR = "2001"


class ResponseCodesLock(Enum):
    SUCCESS = 0


SWITCHABLE_DEVICES = [DeviceTypes.LIGHT, DeviceTypes.MESH_LIGHT, DeviceTypes.PLUG]


class ActionNotSupported(Exception):
    def __init__(self, device_type):
        message = "The action specified is not supported by device type: {}".format(device_type)

        super().__init__(message)


class ParameterError(Exception):
    pass


class AccessTokenError(Exception):
    pass

class LoginError(Exception):
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

        response_json = requests.post("https://auth-prod.api.wyze.com/user/login",
                                      headers=headers, json=login_payload).json()

        # response_json = requests.post("https://auth-prod.api.wyze.com/user/login",
        #                               json=login_payload).json()

        try:
            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']
            return True
        except KeyError as e:
            print(e)
            return False

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

    app_key = "275965684684dbdaf29a0ed9"
    app_secret = "4deekof1ba311c5c33a9cb8e12787e8c"

    def postMethod(self, str, str2, map):
        str4 = str
        str3 = str2
        map2 = map

        return self.getTransferParam(map2, str3, str4, "post")

    def getTransferParam(self, map, str4, str2, str3):
        map["accessToken"] = self.access_token
        map["key"] = self.app_key
        map["timestamp"] = str(datetime.datetime.now().timestamp()).split(".")[0] + "000"
        map["sign"] = self.getSignStr(str4, str3, map)
        import json
        print(json.dumps(map))
        return map

    def getSignStr(self, str, str2, map: Dict):
        string_buf = str2 + str
        for entry in sorted(map.keys()):
            print(entry)
            print(map[entry])
            string_buf += entry + "=" + map[entry] + "&"

        string_buf = string_buf[:-1]
        print(string_buf)
        string_buf += self.app_secret
        import urllib.parse
        urlencoded = urllib.parse.quote_plus(string_buf)
        sign_str = hashlib.md5(urlencoded.encode()).hexdigest()
        print(sign_str)
        return sign_str

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

        print(payload)
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

        response_json = requests.post("https://api.wyzecam.com/app/v2/device/get_property_list",
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
        response_json = requests.post("https://api.wyzecam.com/app/v2/device/set_property", json=payload).json()

        self.check_for_errors(response_json)

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

        response_json = requests.post("https://api.wyzecam.com/app/v2/device/get_event_list", json=payload).json()

        self.check_for_errors(response_json)

        return response_json

    def lock_control(self, device: Device, action: str):
        sb2 = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/control"
        str3 = "/openapi/lock/v1/control"

        uuid = device.mac.split(".")[2]

        hash_map = {
            "uuid": uuid,
            "action": action  # "remoteLock" or "remoteUnlock"
        }

        payload = self.postMethod(sb2, str3, hash_map)

        url = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/control"

        response_json = requests.post(url, json=payload).json()
        print(response_json)
