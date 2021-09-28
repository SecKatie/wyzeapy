#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import json
import time
from typing import List, Tuple, Any, Dict, Optional
import asyncio

from wyzeapy.const import PHONE_SYSTEM_TYPE, APP_VERSION, APP_VER, PHONE_ID, APP_NAME, OLIVE_APP_ID, APP_INFO, SC, SV
from wyzeapy.crypto import olive_create_signature
from wyzeapy.payload_factory import olive_create_hms_patch_payload, olive_create_hms_payload, \
    olive_create_hms_get_payload, ford_create_payload, olive_create_get_payload, olive_create_post_payload, \
    olive_create_user_info_payload
from wyzeapy.services.update_manager import DeviceUpdater, UpdateManager
from wyzeapy.types import PropertyIDs, Device, ThermostatProps
from wyzeapy.utils import check_for_errors_standard, check_for_errors_hms, check_for_errors_lock, \
    check_for_errors_thermostat
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class BaseService:
    _devices: Optional[List[Device]] = None
    _last_updated_time: time = 0  #  preload a value of 0 so that comparison will succeed on the first run
    _min_update_time = 1200  #  lets let the device_params update every 20 minutes for now. This could probably reduced signicficantly.
    _update_lock: asyncio.Lock() = asyncio.Lock()
    _update_manager: UpdateManager = UpdateManager()
    _update_loop = None
    _updater: DeviceUpdater = None

    def __init__(self, auth_lib: WyzeAuthLib):
        self._auth_lib = auth_lib

    async def start_update_manager(self):
        if BaseService._update_loop is None:
            BaseService._update_loop = asyncio.get_event_loop()
            BaseService._update_loop.create_task(BaseService._update_manager.update_next())       

    def register_updater(self, device: Device, interval) -> DeviceUpdater:
        self._dev_updater = DeviceUpdater(self, device, interval)
        BaseService._update_manager.add_updater(self._dev_updater)

    def unregister_updater(self):
        if self._updater:
            BaseService._update_manager.del_updater(self._updater)

    async def set_push_info(self, on: bool) -> None:
        await self._auth_lib.refresh_if_should()

        url = "https://api.wyzecam.com/app/user/set_push_info"
        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "push_switch": "1" if on else "2",
            "sc": SC,
            "ts": int(time.time()),
            "sv": SV,
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        response_json = await self._auth_lib.post(url, json=payload)

        check_for_errors_standard(response_json)

    async def get_user_profile(self) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        payload = olive_create_user_info_payload()
        signature = olive_create_signature(payload, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        url = 'https://wyze-platform-service.wyzecam.com/app/v2/platform/get_user_profile'

        response_json = await self._auth_lib.get(url, headers=headers, params=payload)

        return response_json

    async def get_object_list(self) -> List[Device]:
        """
        Wraps the api.wyzecam.com/app/v2/home_page/get_object_list endpoint

        :return: List of devices
        """
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
        
        # Cache the devices so that update calls can pull more recent device_params 
        BaseService._devices = [Device(device) for device in response_json['data']['device_list']]

        return BaseService._devices

    async def get_updated_params(self, device_mac: str = None) -> Dict[str, Optional[Any]]:
        if time.time() - BaseService._last_updated_time >= BaseService._min_update_time:
            await self.get_object_list()
            BaseService._last_updated_time = time.time()
        ret_params = {}
        for dev in BaseService._devices:
            if dev.mac == device_mac:
                ret_params = dev.device_params
        return ret_params

    async def _get_property_list(self, device: Device) -> List[Tuple[PropertyIDs, Any]]:
        """
        Wraps the api.wyzecam.com/app/v2/device/get_property_list endpoint

        :param device: Device to get properties for
        :return: List of PropertyIDs and values
        """

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
        """
        Wraps the api.wyzecam.com/app/v2/device/set_property_list endpoint

        :param device: The device for which to set the property(ies)
        :param plist: A list of properties [{"pid": pid, "pvalue": pvalue},...]
        :return:
        """

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
            "property_list": plist,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/set_property_list",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _run_action_list(self, device: Device, plist: List[Dict[Any, Any]]) -> None:
        """
        Wraps the api.wyzecam.com/app/v2/auto/run_action_list endpoint

        :param device: The device for which to run the action list
        :param plist: A list of properties [{"pid": pid, "pvalue": pvalue},...]
        """
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

    async def _get_event_list(self, count: int) -> Dict[Any, Any]:
        """
        Wraps the api.wyzecam.com/app/v2/device/get_event_list endpoint

        :param count: Number of events to gather
        :return: Response from the server
        """

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
        """
        Wraps the api.wyzecam.com/app/v2/auto/run_action endpoint

        :param device: The device for which to run the action
        :param action: The action to run
        :return:
        """

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
            "provider_key": device.product_model,
            "instance_id": device.mac,
            "action_key": action,
            "action_params": {},
            "custom_string": "",
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/auto/run_action",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _set_property(self, device: Device, pid: str, pvalue: str) -> None:
        """
        Wraps the api.wyzecam.com/app/v2/device/set_property endpoint

        :param device: The device for which to set the property
        :param pid: The property id
        :param pvalue: The property value
        """
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
            "pvalue": pvalue,
            "pid": pid,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/set_property",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _monitoring_profile_active(self, hms_id: str, home: int, away: int) -> None:
        """
        Wraps the hms.api.wyze.com/api/v1/monitoring/v1/profile/active endpoint

        :param hms_id: The hms id
        :param home: 1 for home 0 for not
        :param away: 1 for away 0 for not
        :return:
        """
        await self._auth_lib.refresh_if_should()

        url = "https://hms.api.wyze.com/api/v1/monitoring/v1/profile/active"
        query = olive_create_hms_patch_payload(hms_id)
        signature = olive_create_signature(query, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature,
            'Authorization': self._auth_lib.token.access_token
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
        response_json = await self._auth_lib.patch(url, headers=headers, params=query, json=payload)
        check_for_errors_hms(response_json)

    async def _get_plan_binding_list_by_user(self) -> Dict[Any, Any]:
        """
        Wraps the wyze-membership-service.wyzecam.com/platform/v2/membership/get_plan_binding_list_by_user endpoint

        :return: The response to gathering the plan for the current user
        """

        if self._auth_lib.should_refresh:
            await self._auth_lib.refresh()

        url = "https://wyze-membership-service.wyzecam.com/platform/v2/membership/get_plan_binding_list_by_user"
        payload = olive_create_hms_payload()
        signature = olive_create_signature(payload, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        response_json = await self._auth_lib.get(url, headers=headers, params=payload)
        check_for_errors_hms(response_json)
        return response_json

    async def _disable_reme_alarm(self, hms_id: str) -> None:
        """
        Wraps the hms.api.wyze.com/api/v1/reme-alarm endpoint

        :param hms_id: The hms_id for the account
        """
        await self._auth_lib.refresh_if_should()

        url = "https://hms.api.wyze.com/api/v1/reme-alarm"
        payload = {
            "hms_id": hms_id,
            "remediation_id": "emergency"
        }
        headers = {
            "Authorization": self._auth_lib.token.access_token
        }

        response_json = await self._auth_lib.delete(url, headers=headers, json=payload)

        check_for_errors_hms(response_json)

    async def _monitoring_profile_state_status(self, hms_id: str) -> Dict[Any, Any]:
        """
        Wraps the hms.api.wyze.com/api/v1/monitoring/v1/profile/state-status endpoint

        :param hms_id: The hms_id
        :return: The response that includes the status
        """
        if self._auth_lib.should_refresh:
            await self._auth_lib.refresh()

        url = "https://hms.api.wyze.com/api/v1/monitoring/v1/profile/state-status"
        query = olive_create_hms_get_payload(hms_id)
        signature = olive_create_signature(query, self._auth_lib.token.access_token)
        headers = {
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature,
            'Authorization': self._auth_lib.token.access_token,
            'Content-Type': "application/json"
        }

        response_json = await self._auth_lib.get(url, headers=headers, params=query)

        check_for_errors_hms(response_json)
        return response_json

    async def _lock_control(self, device: Device, action: str) -> None:
        await self._auth_lib.refresh_if_should()

        url_path = "/openapi/lock/v1/control"

        device_uuid = device.mac.split(".")[2]

        payload = {
            "uuid": device_uuid,
            "action": action  # "remoteLock" or "remoteUnlock"
        }
        payload = ford_create_payload(self._auth_lib.token.access_token, payload, url_path, "post")

        url = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/control"

        response_json = await self._auth_lib.post(url, json=payload)

        check_for_errors_lock(response_json)

    async def _get_lock_info(self, device: Device) -> Dict[str, Optional[Any]]:
        await self._auth_lib.refresh_if_should()

        url_path = "/openapi/lock/v1/info"

        device_uuid = device.mac.split(".")[2]

        payload = {
            "uuid": device_uuid,
            "with_keypad": "1"
        }

        payload = ford_create_payload(self._auth_lib.token.access_token, payload, url_path, "get")

        url = "https://yd-saas-toc.wyzecam.com/openapi/lock/v1/info"

        response_json = await self._auth_lib.get(url, params=payload)

        check_for_errors_lock(response_json)

        return response_json

    async def _get_device_info(self, device: Device) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "device_mac": device.mac,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "device_model": device.product_model,
            "sv": "c86fa16fc99d4d6580f82ef3b942e586",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/get_device_Info",
                                                  json=payload)

        check_for_errors_standard(response_json)

        return response_json

    async def _thermostat_get_iot_prop(self, device: Device) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        payload = olive_create_get_payload(device.mac)
        signature = olive_create_signature(payload, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        url = 'https://wyze-earth-service.wyzecam.com/plugin/earth/get_iot_prop'

        response_json = await self._auth_lib.get(url, headers=headers, params=payload)

        check_for_errors_thermostat(response_json)

        return response_json

    async def _thermostat_set_iot_prop(self, device: Device, prop: ThermostatProps, value: Any) -> None:
        await self._auth_lib.refresh_if_should()

        url = "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic"
        payload = olive_create_post_payload(device.mac, device.product_model, prop, value)
        signature = olive_create_signature(json.dumps(payload, separators=(',', ':')),
                                           self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        payload_str = json.dumps(payload, separators=(',', ':'))

        response_json = await self._auth_lib.post(url, headers=headers, data=payload_str)

        check_for_errors_thermostat(response_json)
