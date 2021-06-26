#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import asyncio
import os
import time
import unittest
from typing import List

from wyzeapy.client import Client
from wyzeapy.types import Device, ThermostatProps, HMSStatus


class TestFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_get_devices_return_type(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        devices = await client.get_devices()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

        await client.async_close()

    async def test_get_plugs(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        devices = await client.get_plugs()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

        await client.async_close()

    async def test_get_cameras(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        devices = await client.get_cameras()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

        await client.async_close()

    async def test_get_locks(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        devices = await client.get_locks()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

        await client.async_close()

    async def test_get_bulbs(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        devices = await client.get_bulbs()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

        await client.async_close()

    async def test_get_info(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_bulb = Device({
            'mac': '7C78B214CF40',
            'product_type': 'MeshLight',
            'product_model': 'WLPA19C'
        })

        await client.get_info(test_bulb)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_turn_on_color_bulb(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_bulb = Device({
            'mac': '7C78B214CF40',
            'product_type': 'MeshLight',
            'product_model': 'WLPA19C'
        })

        await client.turn_on(test_bulb)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_turn_off_color_bulb(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_bulb = Device({
            'mac': '7C78B214CF40',
            'product_type': 'MeshLight',
            'product_model': 'WLPA19C'
        })

        await client.turn_off(test_bulb)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_turn_on_bulb(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_bulb = Device({
            'mac': '2CAA8E325C52',
            'product_type': 'Light',
            'product_model': 'WLPA19'
        })

        await client.turn_on(test_bulb)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_turn_off_bulb(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_bulb = Device({
            'mac': '2CAA8E325C52',
            'product_type': 'Light',
            'product_model': 'WLPA19'
        })

        await client.turn_off(test_bulb)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_unlock_door(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_lock = Device({
            'mac': 'YD.LO1.46c36fcce6c550e527ff79bd8cef59c2',
            'product_type': 'Lock',
            'product_model': 'WLCK1'
        })

        await client.turn_off(test_lock)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_lock_door(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        locks = await client.get_locks()
        print(locks)
        print(locks[0])

        await client.turn_on(locks[0])

        await asyncio.sleep(5)

        await client.async_close()

    async def test_can_read_thermostat(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        test_thermostat = Device({
            'mac': 'CO_EA1_31304635143637394a414e75',
            'product_type': 'Thermostat',
            'product_model': 'CO_EA1'
        })

        info = await client.get_thermostat_info(test_thermostat)

        self.assertIsInstance(info, List)
        for prop, value in info:
            self.assertIsInstance(prop, ThermostatProps)

        await client.async_close()


class TestHMS(unittest.IsolatedAsyncioTestCase):
    async def test_can_get_hms_id(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        device_id = await client.net_client.get_hms_id()

        self.assertEqual(device_id, "c35aecadc9d24e42b799e0be9c2ffc2f")

        await client.async_close()

    async def test_get_hms_status(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        status = await client.get_hms_info()
        self.assertIsInstance(status, HMSStatus)

        await client.async_close()

    async def test_set_hms_status_disarmed(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        await client.set_hms_status(HMSStatus.DISARMED)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_set_hms_status_home(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        await client.set_hms_status(HMSStatus.HOME)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_set_hms_status_away(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        await client.set_hms_status(HMSStatus.AWAY)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_has_hms(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        has_hms = await client.has_hms()

        await asyncio.sleep(5)

        self.assertTrue(has_hms)

        await client.async_close()


class TestEvents(unittest.IsolatedAsyncioTestCase):
    async def test_get_latest_cached_event(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        devices = await client.get_cameras()

        await client.get_cached_latest_event(devices[0])

        await client.async_close()


class TestThermostat(unittest.IsolatedAsyncioTestCase):
    async def test_thermostat(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))
        await client.async_init()

        thermostats = await client.get_thermostats()

        await client.set_thermostat_prop(thermostats[0], ThermostatProps.COOL_SP, 72)

        await asyncio.sleep(5)
