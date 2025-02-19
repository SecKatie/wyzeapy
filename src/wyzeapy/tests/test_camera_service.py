import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.camera_service import CameraService, Camera, DEVICEMGMT_API_MODELS
from wyzeapy.types import DeviceTypes, PropertyIDs, Event
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestCameraService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.camera_service = CameraService(auth_lib=self.mock_auth_lib)
        self.camera_service._get_property_list = AsyncMock()
        self.camera_service._get_event_list = AsyncMock()
        self.camera_service._run_action = AsyncMock()
        self.camera_service._run_action_devicemgmt = AsyncMock()
        self.camera_service._set_property = AsyncMock()
        self.camera_service._set_property_list = AsyncMock()
        self.camera_service._set_toggle = AsyncMock()
        self.camera_service.get_updated_params = AsyncMock()

        # Create a test camera
        self.test_camera = Camera({
            "device_type": DeviceTypes.CAMERA.value,
            "product_model": "WYZEC1",
            "mac": "TEST123",
            "nickname": "Test Camera",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_legacy_camera(self):
        # Mock responses
        self.camera_service._get_event_list.return_value = {
            'data': {
                'event_list': [{
                    'event_ts': 1234567890,
                    'device_mac': 'TEST123',
                    'event_type': 'motion'
                }]
            }
        }
        
        self.camera_service._get_property_list.return_value = [
            (PropertyIDs.AVAILABLE, "1"),
            (PropertyIDs.ON, "1"),
            (PropertyIDs.CAMERA_SIREN, "0"),
            (PropertyIDs.ACCESSORY, "0"),
            (PropertyIDs.NOTIFICATION, "1"),
            (PropertyIDs.MOTION_DETECTION, "1")
        ]

        updated_camera = await self.camera_service.update(self.test_camera)

        self.assertTrue(updated_camera.available)
        self.assertTrue(updated_camera.on)
        self.assertFalse(updated_camera.siren)
        self.assertFalse(updated_camera.floodlight)
        self.assertTrue(updated_camera.notify)
        self.assertTrue(updated_camera.motion)
        self.assertIsNotNone(updated_camera.last_event)
        self.assertEqual(updated_camera.last_event_ts, 1234567890)

    async def test_update_devicemgmt_camera(self):
        # Create a test camera using new API model
        devicemgmt_camera = Camera({
            "device_type": DeviceTypes.CAMERA.value,
            "product_model": "LD_CFP",  # Floodlight pro model
            "mac": "TEST456",
            "nickname": "Test DeviceMgmt Camera",
            "device_params": {"ip": "192.168.1.101"},
            "raw_dict": {}
        })

        self.camera_service._get_iot_prop_devicemgmt = AsyncMock(return_value={
            'data': {
                'capabilities': [
                    {
                        'name': 'camera',
                        'properties': {'motion-detect-recording': True}
                    },
                    {
                        'name': 'floodlight',
                        'properties': {'on': True}
                    },
                    {
                        'name': 'siren',
                        'properties': {'state': True}
                    },
                    {
                        'name': 'iot-device',
                        'properties': {
                            'push-switch': True,
                            'iot-power': True,
                            'iot-state': True
                        }
                    }
                ]
            }
        })

        updated_camera = await self.camera_service.update(devicemgmt_camera)

        self.assertTrue(updated_camera.available)
        self.assertTrue(updated_camera.on)
        self.assertTrue(updated_camera.siren)
        self.assertTrue(updated_camera.floodlight)
        self.assertTrue(updated_camera.notify)
        self.assertTrue(updated_camera.motion)

    async def test_turn_on_off_legacy_camera(self):
        await self.camera_service.turn_on(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(self.test_camera, "power_on")

        await self.camera_service.turn_off(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(self.test_camera, "power_off")

    async def test_siren_control_legacy_camera(self):
        await self.camera_service.siren_on(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(self.test_camera, "siren_on")

        await self.camera_service.siren_off(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(self.test_camera, "siren_off")

    async def test_floodlight_control_legacy_camera(self):
        await self.camera_service.floodlight_on(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera, 
            PropertyIDs.ACCESSORY.value, 
            "1"
        )

        await self.camera_service.floodlight_off(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera, 
            PropertyIDs.ACCESSORY.value, 
            "2"
        )

    async def test_notification_control_legacy_camera(self):
        await self.camera_service.turn_on_notifications(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera,
            PropertyIDs.NOTIFICATION.value,
            "1"
        )

        await self.camera_service.turn_off_notifications(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera,
            PropertyIDs.NOTIFICATION.value,
            "0"
        )

    async def test_motion_detection_control_legacy_camera(self):
        await self.camera_service.turn_on_motion_detection(self.test_camera)
        self.camera_service._set_property.assert_any_await(
            self.test_camera,
            PropertyIDs.MOTION_DETECTION.value,
            "1"
        )
        self.camera_service._set_property.assert_any_await(
            self.test_camera,
            PropertyIDs.MOTION_DETECTION_TOGGLE.value,
            "1"
        )

        await self.camera_service.turn_off_motion_detection(self.test_camera)
        self.camera_service._set_property.assert_any_await(
            self.test_camera,
            PropertyIDs.MOTION_DETECTION.value,
            "0"
        )
        self.camera_service._set_property.assert_any_await(
            self.test_camera,
            PropertyIDs.MOTION_DETECTION_TOGGLE.value,
            "0"
        )

if __name__ == '__main__':
    unittest.main() 