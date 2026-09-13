import unittest
from unittest.mock import AsyncMock, MagicMock, patch
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
        self.motion_sensor = Sensor(
            {
                "product_type": DeviceTypes.MOTION_SENSOR.value,
                "product_model": "PIR3U",
                "mac": "MOTION123",
                "nickname": "Test Motion Sensor",
                "device_params": {"ip": "192.168.1.100"},
                "raw_dict": {},
            }
        )

        self.contact_sensor = Sensor(
            {
                "product_type": DeviceTypes.CONTACT_SENSOR.value,
                "product_model": "DWS3U",
                "mac": "CONTACT456",
                "nickname": "Test Contact Sensor",
                "device_params": {"ip": "192.168.1.101"},
                "raw_dict": {},
            }
        )

        self.leak_sensor = Sensor(
            {
                "product_type": DeviceTypes.LEAK_SENSOR.value,
                "product_model": "WS3U",
                "mac": "LEAK789",
                "nickname": "Test Leak Sensor",
                "device_params": {},
                "raw_dict": {},
            }
        )

        self.temp_humidity_sensor = Sensor(
            {
                "product_type": DeviceTypes.TEMPERATURE_HUMIDITY.value,
                "product_model": "TH3U",
                "mac": "TEMPHUMID321",
                "nickname": "Test Temp/Humidity Sensor",
                "device_params": {},
                "raw_dict": {},
            }
        )

    async def test_update_motion_sensor_detected(self):
        self.sensor_service.get_updated_params.return_value = {"motion_state": 1}

        updated_sensor = await self.sensor_service.update(self.motion_sensor)
        self.assertTrue(updated_sensor.detected)
        self.sensor_service._get_device_info.assert_not_called()

    async def test_update_motion_sensor_not_detected(self):
        self.sensor_service.get_updated_params.return_value = {"motion_state": 0}

        updated_sensor = await self.sensor_service.update(self.motion_sensor)
        self.assertFalse(updated_sensor.detected)
        self.sensor_service._get_device_info.assert_not_called()

    async def test_update_contact_sensor_detected(self):
        self.sensor_service.get_updated_params.return_value = {"open_close_state": 1}

        updated_sensor = await self.sensor_service.update(self.contact_sensor)
        self.assertTrue(updated_sensor.detected)
        self.sensor_service._get_device_info.assert_not_called()

    async def test_update_contact_sensor_not_detected(self):
        self.sensor_service.get_updated_params.return_value = {"open_close_state": 0}

        updated_sensor = await self.sensor_service.update(self.contact_sensor)
        self.assertFalse(updated_sensor.detected)
        self.sensor_service._get_device_info.assert_not_called()
    async def test_update_leak_sensor_detected(self):
        self.sensor_service.get_updated_params.return_value = {
            "ws_detect_state": 1
        }

        updated_sensor = await self.sensor_service.update(self.leak_sensor)
        self.assertTrue(updated_sensor.detected)
        self.sensor_service._get_device_info.assert_not_called()

    async def test_update_leak_sensor_not_detected(self):
        self.sensor_service.get_updated_params.return_value = {
            "ws_detect_state": 0
        }

        updated_sensor = await self.sensor_service.update(self.leak_sensor)
        self.assertFalse(updated_sensor.detected)
        self.sensor_service._get_device_info.assert_not_called()

    async def test_update_temperature_humidity_sensor(self):
        self.sensor_service.get_updated_params.return_value = {
            "th_sensor_temperature": "73.42",
            "th_sensor_humidity": 76,
        }

        updated_sensor = await self.sensor_service.update(self.temp_humidity_sensor)
        self.assertEqual(
            updated_sensor.device_params["th_sensor_temperature"], "73.42"
        )
        self.assertEqual(updated_sensor.device_params["th_sensor_humidity"], 76)
        self.sensor_service._get_device_info.assert_not_called()

    async def test_get_sensors(self):
        mock_motion_device = MagicMock()
        mock_motion_device.type = DeviceTypes.MOTION_SENSOR
        mock_motion_device.raw_dict = {
            "device_type": DeviceTypes.MOTION_SENSOR.value,
            "product_model": "PIR3U",
            "mac": "MOTION123",
        }

        mock_contact_device = MagicMock()
        mock_contact_device.type = DeviceTypes.CONTACT_SENSOR
        mock_contact_device.raw_dict = {
            "device_type": DeviceTypes.CONTACT_SENSOR.value,
            "product_model": "DWS3U",
            "mac": "CONTACT456",
        }

        mock_leak_device = MagicMock()
        mock_leak_device.type = DeviceTypes.LEAK_SENSOR
        mock_leak_device.raw_dict = {
            "device_type": DeviceTypes.LEAK_SENSOR.value,
            "product_model": "WS3U",
            "mac": "LEAK789",
        }

        mock_temp_humidity_device = MagicMock()
        mock_temp_humidity_device.type = DeviceTypes.TEMPERATURE_HUMIDITY
        mock_temp_humidity_device.raw_dict = {
            "device_type": DeviceTypes.TEMPERATURE_HUMIDITY.value,
            "product_model": "TH3U",
            "mac": "TEMPHUMID321",
        }

        self.sensor_service.get_object_list.return_value = [
            mock_motion_device,
            mock_contact_device,
            mock_leak_device,
            mock_temp_humidity_device,
        ]

        sensors = await self.sensor_service.get_sensors()
        self.assertEqual(len(sensors), 4)
        self.assertIsInstance(sensors[0], Sensor)
        self.assertIsInstance(sensors[1], Sensor)
        self.assertIsInstance(sensors[2], Sensor)
        self.assertIsInstance(sensors[3], Sensor)
        self.sensor_service.get_object_list.assert_awaited_once()

    async def test_register_for_updates(self):
        mock_callback = MagicMock()
        await self.sensor_service.register_for_updates(
            self.motion_sensor, mock_callback
        )

        self.assertEqual(len(self.sensor_service._subscribers), 1)
        self.assertEqual(self.sensor_service._subscribers[0][0], self.motion_sensor)
        self.assertEqual(self.sensor_service._subscribers[0][1], mock_callback)

    async def test_deregister_for_updates(self):
        mock_callback = MagicMock()
        await self.sensor_service.register_for_updates(
            self.motion_sensor, mock_callback
        )
        await self.sensor_service.deregister_for_updates(self.motion_sensor)

        self.assertEqual(len(self.sensor_service._subscribers), 0)

    async def test_update_unrecognized_sensor_type_falls_back_to_property_list(self):
        unrecognized_sensor = Sensor(
            {
                "product_type": "SomeFutureSensorType",
                "product_model": "XX1U",
                "mac": "FUTURE999",
                "nickname": "Test Future Sensor",
                "device_params": {},
                "raw_dict": {},
            }
        )
        self.sensor_service._get_device_info.return_value = {
            "data": {"property_list": [{"pid": "unknown_property", "value": "1"}]}
        }

        updated_sensor = await self.sensor_service.update(unrecognized_sensor)
        self.assertFalse(updated_sensor.detected)  # Should maintain default value
        self.sensor_service._get_device_info.assert_called_once()

    async def test_update_worker_sleeps_between_passes(self):
        self.sensor_service._subscribers = [(self.motion_sensor, MagicMock())]
        # Avoid creating a real, never-awaited coroutine from self.update()
        self.sensor_service.update = MagicMock(return_value="unused")

        mock_future = MagicMock()
        mock_future.result.return_value = self.motion_sensor

        with (
            patch(
                "wyzeapy.services.sensor_service.asyncio.run_coroutine_threadsafe",
                return_value=mock_future,
            ),
            patch(
                "wyzeapy.services.sensor_service.time.sleep",
                side_effect=[None, None, RuntimeError("stop loop")],
            ) as mock_sleep,
        ):
            with self.assertRaises(RuntimeError):
                self.sensor_service.update_worker(loop=MagicMock())

        self.assertEqual(mock_sleep.call_count, 3)
        mock_sleep.assert_called_with(self.sensor_service._worker_loop_interval)


if __name__ == "__main__":
    unittest.main()
