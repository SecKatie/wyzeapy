import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.sensor_service import SensorService, Sensor
from wyzeapy.types import DeviceTypes, PropertyIDs
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestSensorService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.sensor_service = SensorService(auth_lib=self.mock_auth_lib)
        self.sensor_service._get_device_info = AsyncMock()
        self.sensor_service.get_updated_params = AsyncMock()
        self.sensor_service.get_object_list = AsyncMock()
        
        # Reset the class-level subscribers list
        self.sensor_service._subscribers = []

        # Create test sensors
        self.motion_sensor = Sensor({
            "device_type": DeviceTypes.MOTION_SENSOR.value,
            "product_model": "PIR3U",
            "mac": "MOTION123",
            "nickname": "Test Motion Sensor",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

        self.contact_sensor = Sensor({
            "device_type": DeviceTypes.CONTACT_SENSOR.value,
            "product_model": "DWS3U",
            "mac": "CONTACT456",
            "nickname": "Test Contact Sensor",
            "device_params": {"ip": "192.168.1.101"},
            "raw_dict": {}
        })

    async def test_update_motion_sensor_detected(self):
        self.sensor_service._get_device_info.return_value = {
            'data': {
                'property_list': [
                    {
                        'pid': PropertyIDs.MOTION_STATE.value,
                        'value': '1'
                    }
                ]
            }
        }

        updated_sensor = await self.sensor_service.update(self.motion_sensor)
        self.assertTrue(updated_sensor.detected)

    async def test_update_motion_sensor_not_detected(self):
        self.sensor_service._get_device_info.return_value = {
            'data': {
                'property_list': [
                    {
                        'pid': PropertyIDs.MOTION_STATE.value,
                        'value': '0'
                    }
                ]
            }
        }

        updated_sensor = await self.sensor_service.update(self.motion_sensor)
        self.assertFalse(updated_sensor.detected)

    async def test_update_contact_sensor_detected(self):
        self.sensor_service._get_device_info.return_value = {
            'data': {
                'property_list': [
                    {
                        'pid': PropertyIDs.CONTACT_STATE.value,
                        'value': '1'
                    }
                ]
            }
        }

        updated_sensor = await self.sensor_service.update(self.contact_sensor)
        self.assertTrue(updated_sensor.detected)

    async def test_update_contact_sensor_not_detected(self):
        self.sensor_service._get_device_info.return_value = {
            'data': {
                'property_list': [
                    {
                        'pid': PropertyIDs.CONTACT_STATE.value,
                        'value': '0'
                    }
                ]
            }
        }

        updated_sensor = await self.sensor_service.update(self.contact_sensor)
        self.assertFalse(updated_sensor.detected)

    async def test_get_sensors(self):
        mock_motion_device = MagicMock()
        mock_motion_device.type = DeviceTypes.MOTION_SENSOR
        mock_motion_device.raw_dict = {
            "device_type": DeviceTypes.MOTION_SENSOR.value,
            "product_model": "PIR3U",
            "mac": "MOTION123"
        }

        mock_contact_device = MagicMock()
        mock_contact_device.type = DeviceTypes.CONTACT_SENSOR
        mock_contact_device.raw_dict = {
            "device_type": DeviceTypes.CONTACT_SENSOR.value,
            "product_model": "DWS3U",
            "mac": "CONTACT456"
        }

        self.sensor_service.get_object_list.return_value = [
            mock_motion_device,
            mock_contact_device
        ]

        sensors = await self.sensor_service.get_sensors()
        
        self.assertEqual(len(sensors), 2)
        self.assertIsInstance(sensors[0], Sensor)
        self.assertIsInstance(sensors[1], Sensor)
        self.sensor_service.get_object_list.assert_awaited_once()

    async def test_register_for_updates(self):
        mock_callback = MagicMock()
        await self.sensor_service.register_for_updates(self.motion_sensor, mock_callback)
        
        self.assertEqual(len(self.sensor_service._subscribers), 1)
        self.assertEqual(self.sensor_service._subscribers[0][0], self.motion_sensor)
        self.assertEqual(self.sensor_service._subscribers[0][1], mock_callback)

    async def test_deregister_for_updates(self):
        mock_callback = MagicMock()
        await self.sensor_service.register_for_updates(self.motion_sensor, mock_callback)
        await self.sensor_service.deregister_for_updates(self.motion_sensor)
        
        self.assertEqual(len(self.sensor_service._subscribers), 0)

    async def test_update_with_unknown_property(self):
        self.sensor_service._get_device_info.return_value = {
            'data': {
                'property_list': [
                    {
                        'pid': 'unknown_property',
                        'value': '1'
                    }
                ]
            }
        }

        updated_sensor = await self.sensor_service.update(self.motion_sensor)
        self.assertFalse(updated_sensor.detected)  # Should maintain default value


if __name__ == '__main__':
    unittest.main()