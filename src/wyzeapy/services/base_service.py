#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import time
from abc import abstractmethod, ABC
from typing import List, Tuple, Any, Dict, Optional

from wyzeapy.wyze_auth_lib import WyzeAuthLib
from wyzeapy.const import PHONE_SYSTEM_TYPE, APP_VERSION, APP_VER, PHONE_ID, APP_NAME
from wyzeapy.exceptions import ActionNotSupported
from wyzeapy.types import PropertyIDs, Device, DeviceTypes
from wyzeapy.utils import check_for_errors_standard


class BaseService(ABC):
    _devices: Optional[List[Device]] = None

    def __init__(self, auth_lib: WyzeAuthLib):
        self._auth_lib = auth_lib

    @abstractmethod
    async def update(self, device):
        pass

    async def _get_devices(self) -> List[Device]:
        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/home_page/get_object_list",
                                                  json=payload)

        check_for_errors_standard(response_json)

        return [Device(device) for device in response_json['data']['device_list']]

    async def _get_info(self, device: Device) -> List[Tuple[PropertyIDs, Any]]:
        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "device_model": device.product_model,
            "device_mac": device.mac,
            "target_pid_list": []
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/get_property_list",
                                                  json=payload)

        check_for_errors_standard(response_json)
        properties = response_json['data']['property_list']

        property_list = []
        for property in properties:
            try:
                property_id = PropertyIDs(property['pid'])
                property_list.append((
                    property_id,
                    property['value']
                ))
            except ValueError:
                pass

        return property_list

    async def _set_property_list(self, device: Device, plist: List[Dict[str, str]]) -> None:
        await self._auth_lib.refresh_if_should()

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
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "property_list": plist,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/set_property_list",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _run_action_list(self, device: Device, plist: List[Dict[Any, Any]]) -> None:
        await self._auth_lib.refresh_if_should()

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
            "access_token": self._auth_lib.token.access_token,
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

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/auto/run_action_list",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _get_full_event_list(self, count: int) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

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
            "access_token": self._auth_lib.token.access_token
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/get_event_list",
                                                  json=payload)

        check_for_errors_standard(response_json)
        return response_json

    async def _run_action(self, device: Device, action: str) -> None:
        await self._auth_lib.refresh_if_should()

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
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "provider_key": device.product_model,
            "instance_id": device.mac,
            "action_key": action,
            "action_params": {},
            "custom_string": "",
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/auto/run_action",
                                                  json=payload)

        check_for_errors_standard(response_json)
