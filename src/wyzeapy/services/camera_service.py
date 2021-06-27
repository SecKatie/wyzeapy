#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from typing import Any

from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device, DeviceTypes


class CameraService(BaseService):
    async def update(self, device: Any):
        pass

    async def get_cameras(self):
        return await self._client.get_cameras()

    async def turn_on(self, camera: Device):
        if camera.type in [
            DeviceTypes.CAMERA
        ]:
            await self._client.net_client.run_action(camera, "power_on")

    async def turn_off(self, camera: Device):
        if camera.type in [
            DeviceTypes.CAMERA
        ]:
            await self._client.net_client.run_action(camera, "power_off")
