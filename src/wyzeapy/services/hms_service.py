#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from enum import Enum
from typing import Optional, Dict, Any

from wyzeapy.wyze_auth_lib import WyzeAuthLib
from wyzeapy.const import OLIVE_APP_ID, APP_INFO, PHONE_ID
from wyzeapy.crypto import olive_create_signature
from wyzeapy.payload_factory import olive_create_hms_get_payload, olive_create_hms_payload, \
    olive_create_hms_patch_payload
from wyzeapy.services.base_service import BaseService
from wyzeapy.utils import check_for_errors_hms


class HMSMode(Enum):
    CHANGING = 'changing'
    DISARMED = 'disarm'
    AWAY = 'away'
    HOME = 'home'


class HMSService(BaseService):
    async def update(self, hms_id: str):
        hms_mode = await self._monitoring_profile_state_status(hms_id)
        return HMSMode(hms_mode['message'])

    def __init__(self, auth_lib: WyzeAuthLib):
        super().__init__(auth_lib)

        self._hms_id = None

    @classmethod
    async def create(cls, auth_lib: WyzeAuthLib):
        hms_service = cls(auth_lib)
        hms_service._hms_id = await hms_service._get_hms_id()

        return hms_service

    @property
    def hms_id(self) -> Optional[str]:
        return self._hms_id

    @property
    async def has_hms(self):
        if self._hms_id is None:
            self._hms_id = self.hms_id

        return self._hms_id is not None

    async def set_mode(self, mode: HMSMode):
        if mode == HMSMode.DISARMED:
            await self._disable_reme_alarm(self.hms_id)
            await self._monitoring_profile_active(self.hms_id, 0, 0)
        elif mode == HMSMode.AWAY:
            await self._monitoring_profile_active(self.hms_id, 0, 1)
        elif mode == HMSMode.HOME:
            await self._monitoring_profile_active(self.hms_id, 1, 0)

    async def _disable_reme_alarm(self, hms_id: str) -> None:
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

    async def _get_plan_binding_list_by_user(self) -> Dict[Any, Any]:
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

    async def _get_hms_id(self) -> Optional[str]:
        await self._auth_lib.refresh_if_should()

        if self._hms_id is not None:
            return self._hms_id

        response = await self._get_plan_binding_list_by_user()
        hms_subs = response['data']

        if len(hms_subs) >= 1:
            for sub in hms_subs:
                if (devices := sub.get('deviceList')) is not None and len(devices) >= 1:
                    for device in devices:
                        self._hms_id = str(device['device_id'])
                        return self._hms_id

        return None

    async def _monitoring_profile_active(self, hms_id: str, home: int, away: int) -> None:
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











