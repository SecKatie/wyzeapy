"""Preserve discovery caching while sharing the cache lookup implementation."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from wyzeapy.services.air_purifier_service import AirPurifierService
from wyzeapy.services.base_service import BaseService
from wyzeapy.services.bulb_service import BulbService
from wyzeapy.services.camera_service import CameraService
from wyzeapy.services.irrigation_service import IrrigationService
from wyzeapy.services.lock_service import LockService
from wyzeapy.services.sensor_service import SensorService
from wyzeapy.services.switch_service import SwitchService
from wyzeapy.services.thermostat_service import ThermostatService
from wyzeapy.services.wall_switch_service import WallSwitchService


DISCOVERY_METHODS = (
    (AirPurifierService, "get_air_purifiers"),
    (BulbService, "get_bulbs"),
    (CameraService, "get_cameras"),
    (IrrigationService, "get_irrigations"),
    (LockService, "get_locks"),
    (SensorService, "get_sensors"),
    (SwitchService, "get_switches"),
    (ThermostatService, "get_thermostats"),
    (WallSwitchService, "get_switches"),
)


class TestServiceDiscovery(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        cache = patch.object(BaseService, "_devices", None)
        cache.start()
        self.addCleanup(cache.stop)

    async def test_missing_inventory_is_fetched_once_even_when_empty(self):
        for service_class, method in DISCOVERY_METHODS:
            with self.subTest(service=service_class.__name__):
                service = service_class(MagicMock())
                service.get_object_list = AsyncMock(return_value=[])
                discover = getattr(service, method)

                self.assertEqual(await discover(), [])
                self.assertEqual(await discover(), [])
                service.get_object_list.assert_awaited_once_with()

    async def test_existing_inventory_avoids_discovery_requests(self):
        BaseService._devices = []
        for service_class, method in DISCOVERY_METHODS:
            with self.subTest(service=service_class.__name__):
                service = service_class(MagicMock())
                service.get_object_list = AsyncMock()

                self.assertEqual(await getattr(service, method)(), [])
                service.get_object_list.assert_not_awaited()

    async def test_failed_discovery_can_be_retried(self):
        for service_class, method in DISCOVERY_METHODS:
            with self.subTest(service=service_class.__name__):
                service = service_class(MagicMock())
                service.get_object_list = AsyncMock(
                    side_effect=[RuntimeError("fake discovery failure"), []]
                )
                discover = getattr(service, method)

                with self.assertRaisesRegex(RuntimeError, "fake discovery failure"):
                    await discover()
                self.assertEqual(await discover(), [])
                self.assertEqual(service.get_object_list.await_count, 2)

    async def test_explicit_refresh_preserves_service_snapshot_behavior(self):
        def inventory(mac):
            return {
                "code": "1",
                "data": {"device_list": [{"mac": mac, "product_type": "Plug"}]},
            }

        auth = SimpleNamespace(
            token=SimpleNamespace(access_token="fake-token"),
            refresh_if_should=AsyncMock(),
            post=AsyncMock(side_effect=[inventory("first"), inventory("second")]),
        )
        service = SwitchService(auth)
        inherited = SwitchService(auth)
        self.assertEqual(
            [device.mac for device in await service.get_switches()], ["first"]
        )
        self.assertEqual(
            [device.mac for device in await inherited.get_switches()], ["first"]
        )

        # Explicit discovery still fetches inventory. Services that previously
        # fetched their own snapshot retain it; inherited inventory stays shared.
        await service.get_object_list()

        self.assertEqual(
            [device.mac for device in await service.get_switches()], ["first"]
        )
        self.assertEqual(
            [device.mac for device in await inherited.get_switches()], ["second"]
        )
        self.assertEqual(auth.post.await_count, 2)
        self.assertEqual(auth.refresh_if_should.await_count, 2)
