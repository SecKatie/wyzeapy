import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.irrigation_service import (
    IrrigationService, Irrigation, Zone
)
from wyzeapy.types import DeviceTypes
from wyzeapy.wyze_auth_lib import WyzeAuthLib

# todo: add tests for irrigation service

class TestIrrigationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.irrigation_service = IrrigationService(auth_lib=self.mock_auth_lib)
        self.irrigation_service._irrigation_get_iot_prop = AsyncMock()
        self.irrigation_service._irrigation_get_zone_by_device = AsyncMock()
        self.irrigation_service.get_object_list = AsyncMock()

        # Create test irrigation
        self.test_irrigation = Irrigation({
            "device_type": DeviceTypes.IRRIGATION.value,
            "product_model": "BS_WK1",
            "mac": "IRRIG123",
            "nickname": "Test Irrigation",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_irrigation(self):
        # Mock IoT properties response
        self.irrigation_service._irrigation_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'RSSI': '-65',
                    'app_version': '1.0.10',
                    'IP': '192.168.1.100',
                    'wifi_mac': '00:11:22:33:44:55',
                    'sn': 'SN123456789',
                    'ssid': 'TestSSID',
                    'iot_state': 'connected'
                }
            }
        }

        # Mock zones response
        self.irrigation_service._irrigation_get_zone_by_device.return_value = {
            'data': {
                'zones': [
                    {
                        'zone_number': 1,
                        'name': 'Zone 1',
                        'enabled': True,
                        'zone_id': 'zone1',
                        'smart_duration': 600
                    },
                    {
                        'zone_number': 2,
                        'name': 'Zone 2',
                        'enabled': True,
                        'zone_id': 'zone2',
                        'smart_duration': 900
                    }
                ]
            }
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)

        # Test IoT properties
        self.assertEqual(updated_irrigation.RSSI, -65)
        self.assertEqual(updated_irrigation.app_version, '1.0.10')
        self.assertEqual(updated_irrigation.IP, '192.168.1.100')
        self.assertEqual(updated_irrigation.wifi_mac, '00:11:22:33:44:55')
        self.assertEqual(updated_irrigation.sn, 'SN123456789')
        self.assertEqual(updated_irrigation.ssid, 'TestSSID')
        self.assertTrue(updated_irrigation.available)

        # Test zones
        self.assertEqual(len(updated_irrigation.zones), 2)
        self.assertEqual(updated_irrigation.zones[0].zone_number, 1)
        self.assertEqual(updated_irrigation.zones[0].name, 'Zone 1')
        self.assertTrue(updated_irrigation.zones[0].enabled)
        self.assertEqual(updated_irrigation.zones[0].smart_duration, 600)
        self.assertEqual(updated_irrigation.zones[1].zone_number, 2)
        self.assertEqual(updated_irrigation.zones[1].name, 'Zone 2')
        self.assertTrue(updated_irrigation.zones[1].enabled)
        self.assertEqual(updated_irrigation.zones[1].smart_duration, 900)

    async def test_get_irrigations(self):
        # Create a mock irrigation device with all required attributes
        mock_irrigation = MagicMock()
        mock_irrigation.type = DeviceTypes.IRRIGATION
        mock_irrigation.product_model = "BS_WK1"
        mock_irrigation.raw_dict = {
            "device_type": DeviceTypes.IRRIGATION.value,
            "product_model": "BS_WK1",
            "mac": "IRRIG123",
            "nickname": "Test Irrigation",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        }

        # Mock the get_object_list to return our mock irrigation device
        self.irrigation_service.get_object_list.return_value = [mock_irrigation]

        # Get the irrigations
        irrigations = await self.irrigation_service.get_irrigations()
        
        # Verify the results
        self.assertEqual(len(irrigations), 1)
        self.assertIsInstance(irrigations[0], Irrigation)
        self.assertEqual(irrigations[0].product_model, "BS_WK1")
        self.assertEqual(irrigations[0].mac, "IRRIG123")
        self.irrigation_service.get_object_list.assert_awaited_once()

    async def test_set_zone_quickrun_duration(self):
        # Setup test irrigation with zones
        self.test_irrigation.zones = [
            Zone({
                'zone_number': 1,
                'name': 'Zone 1',
                'enabled': True,
                'zone_id': 'zone1',
                'smart_duration': 600
            }),
            Zone({
                'zone_number': 2,
                'name': 'Zone 2',
                'enabled': True,
                'zone_id': 'zone2',
                'smart_duration': 900
            })
        ]

        # Test setting quickrun duration for zone 1
        await self.irrigation_service._irrigation_set_zone_quickrun_duration(
            self.test_irrigation, 1, 300
        )
        self.assertEqual(self.test_irrigation.zones[0].quickrun_duration, 300)

        # Test setting quickrun duration for zone 2
        await self.irrigation_service._irrigation_set_zone_quickrun_duration(
            self.test_irrigation, 2, 450
        )
        self.assertEqual(self.test_irrigation.zones[1].quickrun_duration, 450)

    async def test_update_with_invalid_property(self):
        self.irrigation_service._irrigation_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'invalid_property': 'some_value',
                    'RSSI': '-65'
                }
            }
        }

        self.irrigation_service._irrigation_get_zone_by_device.return_value = {
            'data': {
                'zones': []
            }
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)
        self.assertEqual(updated_irrigation.RSSI, -65)
        # Other properties should maintain their default values
        self.assertEqual(updated_irrigation.app_version, "1.0.0")
        self.assertEqual(updated_irrigation.IP, "192.168.1.100")
        self.assertEqual(updated_irrigation.wifi_mac, "00:00:00:00:00:00")
        self.assertEqual(updated_irrigation.sn, "SN123456789")
        self.assertEqual(updated_irrigation.ssid, "ssid")


if __name__ == '__main__':
    unittest.main() 