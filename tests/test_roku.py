#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import asyncio
import os
import time
import unittest

from wyzeapy import Rokuapy
from wyzeapy.services.bulb_service import Bulb, RokuBulbService
from wyzeapy.services.camera_service import RokuCameraService
from wyzeapy.services.switch_service import RokuSwitchService
from wyzeapy.types import DeviceTypes

USERNAME = os.getenv("ROKU_EMAIL")
PASSWORD = os.getenv("ROKU_PASSWORD")


async def login() -> Rokuapy:
    client = await Rokuapy.create()
    await client.login(USERNAME, PASSWORD)
    return client


class TestRokuClient(unittest.IsolatedAsyncioTestCase):
    async def test_login(self):
        client = await Rokuapy.create()
        await client.login(USERNAME, PASSWORD)

    async def test_valid_login(self):
        assert await Rokuapy.valid_login(USERNAME, PASSWORD)

    async def test_notifications_are_on(self):
        client = await login()
        await client.enable_notifications()
        assert await client.notifications_are_on

    async def test_get_device_ids(self):
        client = await login()
        device_ids = await client.unique_device_ids
        for id in device_ids:
            print(id)

    async def test_notifications_on(self):
        client = await login()
        await client.enable_notifications()

    async def test_notifications_off(self):
        client = await login()
        await client.disable_notifications()

    async def test_refresh(self):
        client = await Rokuapy.create()
        await client.login(USERNAME, PASSWORD)
        client._auth_lib.token.last_login_time = time.time() - (65 * 60 * 60)
        bulb_service = await client.bulb_service
        for bulb in await bulb_service.get_bulbs():
            print(bulb.nickname)

        await client.async_close()

    async def test_bulb_service(self):
        client = await login()
        assert type(await client.bulb_service) is RokuBulbService
        await client.async_close()

    async def test_switch_service(self):
        client = await login()
        assert type(await client.switch_service) is RokuSwitchService
        await client.async_close()

    async def test_camera_service(self):
        client = await login()
        assert type(await client.camera_service) is RokuCameraService
        await client.async_close()


class TestRokuBulbService(unittest.IsolatedAsyncioTestCase):
    async def test_get_bulbs(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        for bulb in bulbs:
            print(bulb)

        await client.async_close()

    async def test_turn_on_bulb(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        for bulb in bulbs:
            await bulb_service.turn_on(bulb)

        await client.async_close()

    async def test_turn_off_bulb(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        for bulb in bulbs:
            await bulb_service.turn_off(bulb)
        await client.async_close()

    async def test_set_color_temp(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        for bulb in bulbs:
            await bulb_service.set_color_temp(bulb, 1800)
        await client.async_close()

    async def test_set_color(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        for bulb in bulbs:
            if bulb.type == DeviceTypes.MESH_LIGHT:
                await bulb_service.set_color(bulb, "0000FF")
        await client.async_close()

    async def test_set_brightness(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        brightness_tasks = []
        for bulb in bulbs:
            print(bulb.nickname)
            brightness_tasks.append(bulb_service.set_brightness(bulb, 50))

        await asyncio.gather(*brightness_tasks)
        await client.async_close()

    async def test_update(self):
        client = await login()
        bulb_service = await client.bulb_service
        bulbs = await bulb_service.get_bulbs()
        for bulb in bulbs:
            updated_bulb = await bulb_service.update(bulb)
            self.assertIsInstance(updated_bulb, Bulb)

        await client.async_close()
