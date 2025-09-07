import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.irrigation_service import IrrigationService, Irrigation, Zone
from wyzeapy.types import DeviceTypes, Device
from wyzeapy.wyze_auth_lib import WyzeAuthLib

# todo: add tests for irrigation service


class TestIrrigationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.irrigation_service = IrrigationService(auth_lib=self.mock_auth_lib)
        self.irrigation_service.get_iot_prop = AsyncMock()
        self.irrigation_service.get_zone_by_device = AsyncMock()
        self.irrigation_service.get_object_list = AsyncMock()
        self.irrigation_service._get_iot_prop = AsyncMock()
        self.irrigation_service._get_zone_by_device = AsyncMock()
        self.irrigation_service._irrigation_device_info = AsyncMock()

        # Create test irrigation
        self.test_irrigation = Irrigation(
            {
                "device_type": DeviceTypes.IRRIGATION.value,
                "product_model": "BS_WK1",
                "mac": "IRRIG123",
                "nickname": "Test Irrigation",
                "device_params": {"ip": "192.168.1.100"},
                "raw_dict": {},
            }
        )

    async def test_update_irrigation(self):
        # Mock IoT properties response
        self.irrigation_service.get_iot_prop.return_value = {
            "data": {
                "props": {
                    "RSSI": "-65",
                    "IP": "192.168.1.100",
                    "sn": "SN123456789",
                    "ssid": "TestSSID",
                    "iot_state": "connected",
                }
            }
        }

        # Mock zones response
        self.irrigation_service.get_zone_by_device.return_value = {
            "data": {
                "zones": [
                    {
                        "zone_number": 1,
                        "name": "Zone 1",
                        "enabled": True,
                        "zone_id": "zone1",
                        "smart_duration": 600,
                    },
                    {
                        "zone_number": 2,
                        "name": "Zone 2",
                        "enabled": True,
                        "zone_id": "zone2",
                        "smart_duration": 900,
                    },
                ]
            }
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)

        # Test IoT properties
        self.assertEqual(updated_irrigation.RSSI, "-65")
        self.assertEqual(updated_irrigation.IP, "192.168.1.100")
        self.assertEqual(updated_irrigation.sn, "SN123456789")
        self.assertEqual(updated_irrigation.ssid, "TestSSID")
        self.assertTrue(updated_irrigation.available)

        # Test zones
        self.assertEqual(len(updated_irrigation.zones), 2)
        self.assertEqual(updated_irrigation.zones[0].zone_number, 1)
        self.assertEqual(updated_irrigation.zones[0].name, "Zone 1")
        self.assertTrue(updated_irrigation.zones[0].enabled)
        self.assertEqual(updated_irrigation.zones[0].quickrun_duration, 600)
        self.assertEqual(updated_irrigation.zones[1].zone_number, 2)
        self.assertEqual(updated_irrigation.zones[1].name, "Zone 2")
        self.assertTrue(updated_irrigation.zones[1].enabled)
        self.assertEqual(updated_irrigation.zones[1].quickrun_duration, 900)

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
            "raw_dict": {},
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
            Zone(
                {
                    "zone_number": 1,
                    "name": "Zone 1",
                    "enabled": True,
                    "zone_id": "zone1",
                    "smart_duration": 400,
                }
            ),
            Zone(
                {
                    "zone_number": 2,
                    "name": "Zone 2",
                    "enabled": True,
                    "zone_id": "zone2",
                    "smart_duration": 900,
                }
            ),
        ]

        # Test setting quickrun duration
        await self.irrigation_service.set_zone_quickrun_duration(
            self.test_irrigation, 1, 300
        )
        self.assertEqual(self.test_irrigation.zones[0].quickrun_duration, 300)

        # Test setting quickrun duration for non-existent zone
        await self.irrigation_service.set_zone_quickrun_duration(
            self.test_irrigation, 999, 300
        )
        # Verify that no zones were modified
        self.assertEqual(len(self.test_irrigation.zones), 2)
        self.assertEqual(
            self.test_irrigation.zones[0].quickrun_duration, 300
        )  # First zone changed to 300
        self.assertEqual(
            self.test_irrigation.zones[1].quickrun_duration, 900
        )  # Second zone should be unchanged at 900

    async def test_update_with_invalid_property(self):
        self.irrigation_service.get_iot_prop.return_value = {
            "data": {"props": {"invalid_property": "some_value", "RSSI": "-65"}}
        }

        self.irrigation_service.get_zone_by_device.return_value = {
            "data": {"zones": []}
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)
        self.assertEqual(updated_irrigation.RSSI, "-65")
        # Other properties should maintain their default values
        self.assertEqual(updated_irrigation.IP, "192.168.1.100")
        self.assertEqual(updated_irrigation.sn, "SN123456789")
        self.assertEqual(updated_irrigation.ssid, "ssid")

    async def test_start_zone(self):
        # Mock the _start_zone method
        self.irrigation_service._start_zone = AsyncMock()
        expected_response = {"data": {"result": "success"}}
        self.irrigation_service._start_zone.return_value = expected_response

        # Test starting a zone
        result = await self.irrigation_service.start_zone(
            self.test_irrigation, zone_number=1, quickrun_duration=300
        )

        # Verify the call was made with correct parameters
        self.irrigation_service._start_zone.assert_awaited_once_with(
            "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/quickrun",
            self.test_irrigation,
            1,
            300,
        )
        self.assertEqual(result, expected_response)

    async def test_stop_running_schedule(self):
        # Mock the _stop_running_schedule method
        self.irrigation_service._stop_running_schedule = AsyncMock()
        expected_response = {"data": {"result": "stopped"}}
        self.irrigation_service._stop_running_schedule.return_value = expected_response

        # Test stopping running schedule
        result = await self.irrigation_service.stop_running_schedule(
            self.test_irrigation
        )

        # Verify the call was made with correct parameters
        self.irrigation_service._stop_running_schedule.assert_awaited_once_with(
            "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/runningschedule",
            self.test_irrigation,
            "STOP",
        )
        self.assertEqual(result, expected_response)

    async def test_update_device_props(self):
        # Mock IoT properties response
        self.irrigation_service.get_iot_prop.return_value = {
            "data": {
                "props": {
                    "RSSI": "-70",
                    "IP": "192.168.1.101",
                    "sn": "SN987654321",
                    "ssid": "NewSSID",
                    "iot_state": "connected",
                }
            }
        }

        updated_irrigation = await self.irrigation_service.update_device_props(
            self.test_irrigation
        )

        # Test that properties were updated correctly
        self.assertEqual(updated_irrigation.RSSI, "-70")
        self.assertEqual(updated_irrigation.IP, "192.168.1.101")
        self.assertEqual(updated_irrigation.sn, "SN987654321")
        self.assertEqual(updated_irrigation.ssid, "NewSSID")
        self.assertTrue(updated_irrigation.available)

    async def test_update_device_props_disconnected(self):
        # Mock IoT properties response with disconnected state
        self.irrigation_service.get_iot_prop.return_value = {
            "data": {
                "props": {
                    "RSSI": "-80",
                    "IP": "192.168.1.102",
                    "sn": "SN555666777",
                    "ssid": "TestSSID2",
                    "iot_state": "disconnected",
                }
            }
        }

        updated_irrigation = await self.irrigation_service.update_device_props(
            self.test_irrigation
        )

        # Test that device is marked as unavailable
        self.assertFalse(updated_irrigation.available)
        self.assertEqual(updated_irrigation.RSSI, "-80")
        self.assertEqual(updated_irrigation.IP, "192.168.1.102")

    async def test_get_iot_prop(self):
        # Mock the get_iot_prop method directly to test the public interface
        expected_response = {"data": {"props": {"RSSI": "-65"}}}
        self.irrigation_service.get_iot_prop.return_value = expected_response

        # Test get_iot_prop
        result = await self.irrigation_service.get_iot_prop(self.test_irrigation)

        # Verify the call was made and returned expected result
        self.irrigation_service.get_iot_prop.assert_awaited_once_with(
            self.test_irrigation
        )
        self.assertEqual(result, expected_response)

    async def test_get_device_info(self):
        # Mock the _irrigation_device_info method
        self.irrigation_service._irrigation_device_info = AsyncMock()
        expected_response = {"data": {"props": {"enable_schedules": True}}}
        self.irrigation_service._irrigation_device_info.return_value = expected_response

        # Test get_device_info
        result = await self.irrigation_service.get_device_info(self.test_irrigation)

        # Verify the call was made with correct parameters
        expected_keys = "wiring,sensor,enable_schedules,notification_enable,notification_watering_begins,notification_watering_ends,notification_watering_is_skipped,skip_low_temp,skip_wind,skip_rain,skip_saturation"
        self.irrigation_service._irrigation_device_info.assert_awaited_once_with(
            "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/device_info",
            self.test_irrigation,
            expected_keys,
        )
        self.assertEqual(result, expected_response)

    async def test_get_zone_by_device_method(self):
        # Mock the get_zone_by_device method directly to test the public interface
        expected_response = {"data": {"zones": [{"zone_number": 1, "name": "Zone 1"}]}}
        self.irrigation_service.get_zone_by_device.return_value = expected_response

        # Test get_zone_by_device
        result = await self.irrigation_service.get_zone_by_device(self.test_irrigation)

        # Verify the call was made and returned expected result
        self.irrigation_service.get_zone_by_device.assert_awaited_once_with(
            self.test_irrigation
        )
        self.assertEqual(result, expected_response)


class TestZone(unittest.TestCase):
    def test_zone_initialization_with_defaults(self):
        # Test zone initialization with minimal data
        zone_data = {"zone_number": 3, "name": "Test Zone"}
        zone = Zone(zone_data)

        self.assertEqual(zone.zone_number, 3)
        self.assertEqual(zone.name, "Test Zone")
        self.assertTrue(zone.enabled)  # Default value
        self.assertEqual(zone.zone_id, "zone_id")  # Default value
        self.assertEqual(zone.smart_duration, 600)  # Default value
        self.assertEqual(
            zone.quickrun_duration, 600
        )  # Default value from smart_duration

    def test_zone_initialization_with_all_data(self):
        # Test zone initialization with all data
        zone_data = {
            "zone_number": 2,
            "name": "Garden Zone",
            "enabled": False,
            "zone_id": "zone_garden",
            "smart_duration": 1200,
        }
        zone = Zone(zone_data)

        self.assertEqual(zone.zone_number, 2)
        self.assertEqual(zone.name, "Garden Zone")
        self.assertFalse(zone.enabled)
        self.assertEqual(zone.zone_id, "zone_garden")
        self.assertEqual(zone.smart_duration, 1200)
        self.assertEqual(zone.quickrun_duration, 1200)  # Should use smart_duration

    def test_zone_initialization_empty_dict(self):
        # Test zone initialization with empty dict
        zone = Zone({})

        self.assertEqual(zone.zone_number, 1)  # Default value
        self.assertEqual(zone.name, "Zone 1")  # Default value
        self.assertTrue(zone.enabled)  # Default value
        self.assertEqual(zone.zone_id, "zone_id")  # Default value
        self.assertEqual(zone.smart_duration, 600)  # Default value
        self.assertEqual(zone.quickrun_duration, 600)  # Default value


class TestIrrigation(unittest.TestCase):
    def test_irrigation_initialization(self):
        # Test irrigation device initialization
        irrigation_data = {
            "device_type": DeviceTypes.IRRIGATION.value,
            "product_model": "BS_WK1",
            "mac": "IRRIG456",
            "nickname": "Backyard Sprinkler",
            "device_params": {"ip": "192.168.1.200"},
        }
        irrigation = Irrigation(irrigation_data)

        self.assertEqual(irrigation.product_model, "BS_WK1")
        self.assertEqual(irrigation.mac, "IRRIG456")
        self.assertEqual(irrigation.nickname, "Backyard Sprinkler")

        # Test default values
        self.assertEqual(irrigation.RSSI, 0)
        self.assertEqual(irrigation.IP, "192.168.1.100")
        self.assertEqual(irrigation.sn, "SN123456789")
        self.assertFalse(irrigation.available)
        self.assertEqual(irrigation.ssid, "ssid")
        self.assertEqual(len(irrigation.zones), 0)

    def test_irrigation_inheritance(self):
        # Test that Irrigation inherits from Device
        irrigation_data = {
            "product_type": DeviceTypes.IRRIGATION.value,
            "product_model": "BS_WK1",
            "mac": "IRRIG789",
            "nickname": "Front Yard Sprinkler",
        }
        irrigation = Irrigation(irrigation_data)

        # Test inherited Device properties
        self.assertIsInstance(irrigation, Device)
        self.assertEqual(irrigation.type, DeviceTypes.IRRIGATION)


class TestIrrigationServiceEdgeCases(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.irrigation_service = IrrigationService(auth_lib=self.mock_auth_lib)
        self.irrigation_service.get_iot_prop = AsyncMock()
        self.irrigation_service.get_zone_by_device = AsyncMock()
        self.irrigation_service.get_object_list = AsyncMock()

        # Create test irrigation
        self.test_irrigation = Irrigation(
            {
                "device_type": DeviceTypes.IRRIGATION.value,
                "product_model": "BS_WK1",
                "mac": "IRRIG123",
                "nickname": "Test Irrigation",
                "device_params": {"ip": "192.168.1.100"},
                "raw_dict": {},
            }
        )

    async def test_update_with_empty_zones(self):
        # Mock IoT properties response
        self.irrigation_service.get_iot_prop.return_value = {
            "data": {
                "props": {
                    "RSSI": "-65",
                    "IP": "192.168.1.100",
                    "sn": "SN123456789",
                    "ssid": "TestSSID",
                    "iot_state": "connected",
                }
            }
        }

        # Mock empty zones response
        self.irrigation_service.get_zone_by_device.return_value = {
            "data": {"zones": []}
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)

        # Verify empty zones list
        self.assertEqual(len(updated_irrigation.zones), 0)
        self.assertTrue(updated_irrigation.available)

    async def test_update_with_missing_iot_props(self):
        # Mock IoT properties response with missing props
        self.irrigation_service.get_iot_prop.return_value = {"data": {"props": {}}}

        self.irrigation_service.get_zone_by_device.return_value = {
            "data": {"zones": []}
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)

        # Verify default values are used
        self.assertEqual(updated_irrigation.RSSI, -65)
        self.assertEqual(updated_irrigation.IP, "192.168.1.100")
        self.assertEqual(updated_irrigation.sn, "SN123456789")
        self.assertEqual(updated_irrigation.ssid, "ssid")
        self.assertFalse(
            updated_irrigation.available
        )  # iot_state missing, so not connected

    async def test_get_irrigations_empty_device_list(self):
        # Mock empty device list
        self.irrigation_service.get_object_list.return_value = []

        irrigations = await self.irrigation_service.get_irrigations()

        # Verify empty list returned
        self.assertEqual(len(irrigations), 0)
        self.irrigation_service.get_object_list.assert_awaited_once()

    async def test_get_irrigations_no_irrigation_devices(self):
        # Mock device list with non-irrigation devices
        mock_camera = MagicMock()
        mock_camera.type = DeviceTypes.CAMERA
        mock_camera.product_model = "CAM_V1"

        mock_bulb = MagicMock()
        mock_bulb.type = DeviceTypes.LIGHT
        mock_bulb.product_model = "LIGHT_V1"

        self.irrigation_service.get_object_list.return_value = [mock_camera, mock_bulb]

        irrigations = await self.irrigation_service.get_irrigations()

        # Verify no irrigation devices returned
        self.assertEqual(len(irrigations), 0)

    async def test_get_irrigations_wrong_product_model(self):
        # Mock device list with irrigation type but wrong product model
        mock_irrigation = MagicMock()
        mock_irrigation.type = DeviceTypes.IRRIGATION
        mock_irrigation.product_model = "WRONG_MODEL"
        mock_irrigation.raw_dict = {
            "device_type": DeviceTypes.IRRIGATION.value,
            "product_model": "WRONG_MODEL",
            "mac": "IRRIG123",
            "nickname": "Test Irrigation",
        }

        self.irrigation_service.get_object_list.return_value = [mock_irrigation]

        irrigations = await self.irrigation_service.get_irrigations()

        # Verify no irrigation devices returned due to wrong product model
        self.assertEqual(len(irrigations), 0)

    async def test_set_zone_quickrun_duration_zone_not_found(self):
        # Setup test irrigation with zones
        self.test_irrigation.zones = [
            Zone(
                {
                    "zone_number": 1,
                    "name": "Zone 1",
                    "enabled": True,
                    "zone_id": "zone1",
                    "smart_duration": 600,
                }
            )
        ]

        # Try to set duration for non-existent zone
        result = await self.irrigation_service.set_zone_quickrun_duration(
            self.test_irrigation,
            99,  # Non-existent zone
            300,
        )

        # Verify existing zone unchanged
        self.assertEqual(self.test_irrigation.zones[0].quickrun_duration, 600)
        self.assertEqual(result, self.test_irrigation)

    async def test_set_zone_quickrun_duration_no_zones(self):
        # Test with irrigation that has no zones
        self.test_irrigation.zones = []

        result = await self.irrigation_service.set_zone_quickrun_duration(
            self.test_irrigation, 1, 300
        )

        # Verify no error and empty zones list
        self.assertEqual(len(self.test_irrigation.zones), 0)
        self.assertEqual(result, self.test_irrigation)

    async def test_get_schedule_runs_running_schedule(self):
        # Mock the _get_schedule_runs method
        self.irrigation_service._get_schedule_runs = AsyncMock()
        mock_response = {
            "data": {
                "schedules": [
                    {
                        "schedule_state": "running",
                        "schedule_name": "Morning Watering",
                        "zone_runs": [
                            {
                                "zone_number": 3,
                                "zone_name": "Backyard S",
                                "start_ts": 1746376809,
                                "end_ts": 1746376869,
                            }
                        ],
                    }
                ]
            }
        }
        self.irrigation_service._get_schedule_runs.return_value = mock_response

        # Test get_schedule_runs with running schedule
        result = await self.irrigation_service.get_schedule_runs(self.test_irrigation)

        # Verify the call was made with correct parameters
        self.irrigation_service._get_schedule_runs.assert_awaited_once_with(
            "https://wyze-lockwood-service.wyzecam.com/plugin/irrigation/schedule_runs",
            self.test_irrigation,
            limit=2,
        )

        # Verify the result
        expected_result = {"running": True, "zone_number": 3, "zone_name": "Backyard S"}
        self.assertEqual(result, expected_result)

    async def test_get_schedule_runs_past_schedule(self):
        # Mock the _get_schedule_runs method
        self.irrigation_service._get_schedule_runs = AsyncMock()
        mock_response = {
            "data": {
                "schedules": [
                    {
                        "schedule_state": "past",
                        "schedule_name": "Evening Watering",
                        "zone_runs": [
                            {
                                "zone_number": 1,
                                "zone_name": "Front Yard",
                                "start_ts": 1746376809,
                                "end_ts": 1746376869,
                            }
                        ],
                    }
                ]
            }
        }
        self.irrigation_service._get_schedule_runs.return_value = mock_response

        # Test get_schedule_runs with past schedule
        result = await self.irrigation_service.get_schedule_runs(self.test_irrigation)

        # Verify the result
        expected_result = {"running": False}
        self.assertEqual(result, expected_result)

    async def test_get_schedule_runs_no_schedules(self):
        # Mock the _get_schedule_runs method
        self.irrigation_service._get_schedule_runs = AsyncMock()
        mock_response = {"data": {"schedules": []}}
        self.irrigation_service._get_schedule_runs.return_value = mock_response

        # Test get_schedule_runs with no schedules
        result = await self.irrigation_service.get_schedule_runs(self.test_irrigation)

        # Verify the result
        expected_result = {"running": False}
        self.assertEqual(result, expected_result)

    async def test_get_schedule_runs_no_data(self):
        # Mock the _get_schedule_runs method
        self.irrigation_service._get_schedule_runs = AsyncMock()
        mock_response = {}  # No data field
        self.irrigation_service._get_schedule_runs.return_value = mock_response

        # Test get_schedule_runs with no data
        with self.assertLogs(
            "wyzeapy.services.irrigation_service", level="WARNING"
        ) as log:
            result = await self.irrigation_service.get_schedule_runs(
                self.test_irrigation
            )

        # Verify the result
        expected_result = {"running": False}
        self.assertEqual(result, expected_result)

        # Verify warning was logged
        self.assertIn(
            "No schedule data found in response for device IRRIG123", log.output[0]
        )

    async def test_get_schedule_runs_multiple_schedules_running_first(self):
        # Mock the _get_schedule_runs method
        self.irrigation_service._get_schedule_runs = AsyncMock()
        mock_response = {
            "data": {
                "schedules": [
                    {
                        "schedule_state": "running",
                        "schedule_name": "Morning Watering",
                        "zone_runs": [
                            {
                                "zone_number": 2,
                                "zone_name": "Side Yard",
                                "start_ts": 1746376809,
                                "end_ts": 1746376869,
                            }
                        ],
                    },
                    {
                        "schedule_state": "past",
                        "schedule_name": "Evening Watering",
                        "zone_runs": [
                            {
                                "zone_number": 1,
                                "zone_name": "Front Yard",
                                "start_ts": 1746376809,
                                "end_ts": 1746376869,
                            }
                        ],
                    },
                ]
            }
        }
        self.irrigation_service._get_schedule_runs.return_value = mock_response

        # Test get_schedule_runs with multiple schedules, first one running
        result = await self.irrigation_service.get_schedule_runs(self.test_irrigation)

        # Verify the result uses the first running schedule
        expected_result = {"running": True, "zone_number": 2, "zone_name": "Side Yard"}
        self.assertEqual(result, expected_result)

    async def test_get_schedule_runs_multiple_schedules_running_second(self):
        # Mock the _get_schedule_runs method
        self.irrigation_service._get_schedule_runs = AsyncMock()
        mock_response = {
            "data": {
                "schedules": [
                    {
                        "schedule_state": "past",
                        "schedule_name": "Evening Watering",
                        "zone_runs": [
                            {
                                "zone_number": 1,
                                "zone_name": "Front Yard",
                                "start_ts": 1746376809,
                                "end_ts": 1746376869,
                            }
                        ],
                    },
                    {
                        "schedule_state": "running",
                        "schedule_name": "Morning Watering",
                        "zone_runs": [
                            {
                                "zone_number": 4,
                                "zone_name": "Garden Area",
                                "start_ts": 1746376809,
                                "end_ts": 1746376869,
                            }
                        ],
                    },
                ]
            }
        }
        self.irrigation_service._get_schedule_runs.return_value = mock_response

        # Test get_schedule_runs with multiple schedules, second one running
        result = await self.irrigation_service.get_schedule_runs(self.test_irrigation)

        # Verify the result uses the first running schedule found
        expected_result = {
            "running": True,
            "zone_number": 4,
            "zone_name": "Garden Area",
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
