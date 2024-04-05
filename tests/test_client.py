#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
import asyncio
import os
import time
import unittest

from wyzeapy import Wyzeapy
from wyzeapy.services.bulb_service import Bulb, BulbService
from wyzeapy.services.camera_service import Camera, CameraService
from wyzeapy.services.hms_service import HMSService, HMSMode
from wyzeapy.services.lock_service import Lock
from wyzeapy.services.sensor_service import Sensor, SensorService
from wyzeapy.services.switch_service import Switch, SwitchService
from wyzeapy.services.thermostat_service import Thermostat, Preset, HVACState, ThermostatService, HVACMode, FanMode, \
    TemperatureUnit
from wyzeapy.types import DeviceTypes

USERNAME = os.getenv("WYZE_EMAIL")
PASSWORD = os.getenv("WYZE_PASSWORD")


async def login() -> Wyzeapy:
    client = await Wyzeapy.create()
    await client.login(USERNAME, PASSWORD)
    return client


class TestWyzeClient(unittest.IsolatedAsyncioTestCase):
    async def test_login(self):
        client = await Wyzeapy.create()
        await client.login(USERNAME, PASSWORD)
        await client.async_close()

    async def test_valid_login(self):
        assert await Wyzeapy.valid_login(USERNAME, PASSWORD)

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
        client = await Wyzeapy.create()
        await client.login(USERNAME, PASSWORD)
        client._auth_lib.token.last_login_time = time.time() - (65 * 60 * 60)
        bulb_service = await client.bulb_service
        for bulb in await bulb_service.get_bulbs():
            print(bulb.nickname)

        await client.async_close()

    async def test_bulb_service(self):
        client = await login()
        assert type(await client.bulb_service) is BulbService
        await client.async_close()

    async def test_switch_service(self):
        client = await login()
        assert type(await client.switch_service) is SwitchService
        await client.async_close()

    async def test_camera_service(self):
        client = await login()
        assert type(await client.camera_service) is CameraService
        await client.async_close()

    async def test_thermostat_service(self):
        client = await login()
        assert type(await client.thermostat_service) is ThermostatService
        await client.async_close()

    async def hms_service(self):
        client = await login()
        assert type(await client.hms_service) is HMSService
        await client.async_close()

    async def sensor_service(self):
        client = await login()
        assert type(await client.sensor_service) is SensorService
        await client.async_close()


class TestBulbService(unittest.IsolatedAsyncioTestCase):
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


class TestSwitchService(unittest.IsolatedAsyncioTestCase):
    async def test_get_switches(self):
        client = await login()
        switch_service = await client.switch_service
        switches = await switch_service.get_switches()
        for switch in switches:
            print(switch.nickname)

        await client.async_close()

    async def test_turn_on_switch(self):
        client = await login()
        switch_service = await client.switch_service
        switches = await switch_service.get_switches()
        for switch in switches:
            if switch.nickname != 'Air Conditioner':
                await switch_service.turn_on(switch)

        await client.async_close()

    async def test_turn_off_switch(self):
        client = await login()
        switch_service = await client.switch_service
        switches = await switch_service.get_switches()
        for switch in switches:
            if switch.nickname != 'Air Conditioner':
                await switch_service.turn_off(switch)

        await client.async_close()

    async def test_update(self):
        client = await login()
        switch_service = await client.switch_service
        switches = await switch_service.get_switches()
        for switch in switches:
            updated_switch = await switch_service.update(switch)
            self.assertIsInstance(updated_switch, Switch)

        await client.async_close()


class TestCameraService(unittest.IsolatedAsyncioTestCase):
    async def test_get_cameras(self):
        client = await login()
        camera_service = await client.camera_service
        cameras = await camera_service.get_cameras()
        for camera in cameras:
            print(camera.nickname)

        await client.async_close()

    async def test_turn_on_cameras(self):
        client = await login()
        camera_service = await client.camera_service
        cameras = await camera_service.get_cameras()
        for camera in cameras:
            await camera_service.turn_on(camera)
        await client.async_close()

    async def test_turn_off_cameras(self):
        client = await login()
        camera_service = await client.camera_service
        cameras = await camera_service.get_cameras()
        for camera in cameras:
            await camera_service.turn_off(camera)
        await client.async_close()

    async def test_turn_on_notifications(self):
        client = await login()
        camera_service = await client.camera_service
        cameras = await camera_service.get_cameras()
        for camera in cameras:
            await camera_service.turn_on_notifications(camera)
        await client.async_close()

    async def test_turn_off_notifications(self):
        client = await login()
        camera_service = await client.camera_service
        cameras = await camera_service.get_cameras()
        for camera in cameras:
            await camera_service.turn_off_notifications(camera)
        await client.async_close()

    async def test_update(self):
        client = await login()
        camera_service = await client.camera_service
        cameras = await camera_service.get_cameras()
        for camera in cameras:
            updated_camera = await camera_service.update(camera)
            self.assertIsInstance(updated_camera, Camera)

        await client.async_close()


class TestThermostatService(unittest.IsolatedAsyncioTestCase):
    async def test_get_thermostat(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            print(thermostat.nickname)

        await client.async_close()

    async def test_set_cool_point(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            await thermostat_service.set_cool_point(thermostat, 74)

        await client.async_close()

    async def test_set_heat_point(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            await thermostat_service.set_heat_point(thermostat, 64)

        await client.async_close()

    async def test_set_hvac_mode(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            await thermostat_service.set_hvac_mode(thermostat, HVACMode.AUTO)

        await client.async_close()

    async def test_set_fan_mode(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            await thermostat_service.set_fan_mode(thermostat, FanMode.AUTO)

        await client.async_close()

    async def test_set_preset(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            await thermostat_service.set_preset(thermostat, Preset.HOME)

        await client.async_close()

    async def test_update(self):
        client = await login()
        thermostat_service = await client.thermostat_service
        thermostats = await thermostat_service.get_thermostats()
        for thermostat in thermostats:
            updated_thermostat = await thermostat_service.update(thermostat)
            self.assertIsInstance(updated_thermostat, Thermostat)
            self.assertIsInstance(updated_thermostat.cool_set_point, int)
            self.assertIsInstance(updated_thermostat.heat_set_point, int)
            self.assertIsInstance(updated_thermostat.fan_mode, FanMode)
            self.assertIsInstance(updated_thermostat.hvac_mode, HVACMode)
            self.assertIsInstance(updated_thermostat.preset, Preset)
            self.assertIsInstance(updated_thermostat.temperature, float)
            self.assertIsInstance(updated_thermostat.available, bool)
            self.assertIsInstance(updated_thermostat.humidity, int)
            self.assertIsInstance(updated_thermostat.hvac_state, HVACState)
            self.assertIsInstance(updated_thermostat.temp_unit, TemperatureUnit)

        await client.async_close()


class TestHMSService(unittest.IsolatedAsyncioTestCase):
    async def test_get_hms_id(self):
        client = await login()
        hms_service = await client.hms_service
        hms_id = hms_service.hms_id
        assert hms_id == "c35aecadc9d24e42b799e0be9c2ffc2f"

        await client.async_close()

    async def test_has_hms(self):
        client = await login()
        hms_service = await client.hms_service
        hms = await hms_service.has_hms
        assert hms

        await client.async_close()

    async def test_set_hms_disabled(self):
        client = await login()
        hms_service = await client.hms_service
        await hms_service.set_mode(HMSMode.DISARMED)

        await client.async_close()

    async def test_update(self):
        client = await login()
        hms_service = await client.hms_service
        hms_mode = await hms_service.update(hms_service.hms_id)
        self.assertIsInstance(hms_mode, HMSMode)
        await client.async_close()


class TestSensorService(unittest.IsolatedAsyncioTestCase):
    async def test_get_sensors(self):
        client = await login()
        sensor_service = await client.sensor_service
        sensors = await sensor_service.get_sensors()
        for sensor in sensors:
            print(sensor.nickname)

        await client.async_close()

    async def test_update(self):
        client = await login()
        sensor_service = await client.sensor_service
        sensors = await sensor_service.get_sensors()
        for sensor in sensors:
            sensor = await sensor_service.update(sensor)
            self.assertIsInstance(sensor, Sensor)
            self.assertIsInstance(sensor.detected, bool)

        await client.async_close()


class TestLockService(unittest.IsolatedAsyncioTestCase):
    async def test_get_locks(self):
        client = await login()
        lock_service = await client.lock_service
        sensors = await lock_service.get_locks()
        for sensor in sensors:
            print(sensor.nickname)

        await client.async_close()

    async def test_update(self):
        client = await login()
        lock_service = await client.lock_service
        locks = await lock_service.get_locks()
        for lock in locks:
            lock = await lock_service.update(lock)
            self.assertIsInstance(lock, Lock)
            self.assertIsInstance(lock.unlocked, bool)
            self.assertIsInstance(lock.available, bool)
            self.assertIsInstance(lock.door_open, bool)

        await client.async_close()

    async def test_lock(self):
        client = await login()
        lock_service = await client.lock_service
        locks = await lock_service.get_locks()
        for lock in locks:
            await lock_service.lock(lock)

        await asyncio.sleep(5)

        await client.async_close()

    async def test_unlock(self):
        client = await login()
        lock_service = await client.lock_service
        locks = await lock_service.get_locks()
        for lock in locks:
            await lock_service.unlock(lock)

        await asyncio.sleep(5)

        await client.async_close()
