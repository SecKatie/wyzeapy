#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from enum import Enum
from typing import Optional

from wyzeapy import Client
from wyzeapy.services.base_service import BaseService


class HMSMode(Enum):
    CHANGING = 'changing'
    DISARMED = 'disarm'
    AWAY = 'away'
    HOME = 'home'


class HMSService(BaseService):
    async def update(self, hms_id: str):
        hms_mode = await self._client.net_client.monitoring_profile_state_status(hms_id)
        return HMSMode(hms_mode['message'])

    def __init__(self, client: Client):
        super().__init__(client)

        self._hms_id = None

    @property
    async def hms_id(self) -> Optional[str]:
        self._hms_id = await self._client.net_client.get_hms_id()

        return self._hms_id

    @property
    async def has_hms(self):
        if self._hms_id is None:
            self._hms_id = await self.hms_id

        return self._hms_id is not None

    async def set_mode(self, mode: HMSMode):
        if mode == HMSMode.DISARMED:
            await self._client.net_client.disable_reme_alarm(await self.hms_id)
            await self._client.net_client.monitoring_profile_active(await self.hms_id, 0, 0)
        elif mode == HMSMode.AWAY:
            await self._client.net_client.monitoring_profile_active(await self.hms_id, 0, 1)
        elif mode == HMSMode.HOME:
            await self._client.net_client.monitoring_profile_active(await self.hms_id, 1, 0)
