#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy

import os
import unittest
from typing import List

from src.wyzeapy.client import Client
from src.wyzeapy.types import Device, ThermostatProps


class TestLogin(unittest.TestCase):
    def test_can_login(self):
        client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))

        self.assertTrue(client.valid_login)

    def test_bad_login(self):
        client = Client("BadEmail@example.com", "BadPassword123")

        self.assertFalse(client.valid_login)


class TestFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))

    def test_get_devices_return_type(self):
        devices = self._client.get_devices()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

    def test_get_plugs(self):
        devices = self._client.get_plugs()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

    def test_get_cameras(self):
        devices = self._client.get_cameras()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

    def test_get_locks(self):
        devices = self._client.get_locks()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

    def test_get_bulbs(self):
        devices = self._client.get_bulbs()
        self.assertIsInstance(devices, List)
        for device in devices:
            self.assertIsInstance(device, Device)

    def test_turn_on_color_bulb(self):
        test_bulb = Device({
            'mac': '7C78B214CF40',
            'product_type': 'MeshLight',
            'product_model': 'WLPA19C'
        })

        self._client.turn_on(test_bulb)

    def test_turn_off_color_bulb(self):
        test_bulb = Device({
            'mac': '7C78B214CF40',
            'product_type': 'MeshLight',
            'product_model': 'WLPA19C'
        })

        self._client.turn_off(test_bulb)

    def test_turn_on_bulb(self):
        test_bulb = Device({
            'mac': '2CAA8E325C52',
            'product_type': 'Light',
            'product_model': 'WLPA19'
        })

        self._client.turn_on(test_bulb)

    def test_turn_off_bulb(self):
        test_bulb = Device({
            'mac': '2CAA8E325C52',
            'product_type': 'Light',
            'product_model': 'WLPA19'
        })

        self._client.turn_off(test_bulb)

    def test_unlock_door(self):
        test_lock = Device({
            'mac': 'YD.LO1.46c36fcce6c550e527ff79bd8cef59c2',
            'product_type': 'Lock',
            'product_model': 'WLCK1'
        })

        self._client.turn_off(test_lock)

    def test_lock_door(self):
        test_lock = Device({
            'mac': 'YD.LO1.46c36fcce6c550e527ff79bd8cef59c2',
            'product_type': 'Lock',
            'product_model': 'WLCK1'
        })

        self._client.turn_on(test_lock)

    def test_can_read_thermostat(self):
        test_thermostat = Device({
            'mac': 'CO_EA1_31304635143637394a414e75',
            'product_type': 'Thermostat',
            'product_model': 'CO_EA1'
        })

        info = self._client.get_thermostat_info(test_thermostat)

        self.assertIsInstance(info, List)
        for prop, value in info:
            self.assertIsInstance(prop, ThermostatProps)


class TestHMS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = Client(os.getenv("WYZE_EMAIL"), os.getenv("WYZE_PASSWORD"))

    def test_can_get_hms_id(self):
        device_id = self._client.net_client.get_hms_id()

        self.assertEqual(device_id, "c35aecadc9d24e42b799e0be9c2ffc2f")

    def test_can_set_hms_status(self):
        device_id = self._client.net_client.get_hms_id()
        response = self._client.net_client.monitoring_profile_active(device_id, 0, 0)
        self.assertEqual(response['status'], 200)

    def test_can_get_hms_status(self):
        device_id = self._client.net_client.get_hms_id()
        response = self._client.net_client.monitoring_profile_state_status(device_id)
        print(response)
        self.assertEqual(response['status'], 200)
