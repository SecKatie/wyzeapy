#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from enum import Enum
from typing import Optional

from wyzeapy.wyze_auth_lib import WyzeAuthLib
from wyzeapy.services.base_service import BaseService


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

    async def _get_hms_id(self) -> Optional[str]:
        """
        Processes the response from _get_plan_binding_list_by_user to get the hms_id

        :return: The hms_id or nothing if there is no hms in the account
        """

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









