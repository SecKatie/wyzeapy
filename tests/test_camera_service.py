import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from wyzeapy.services.camera_service import CameraService, Camera
from wyzeapy.types import DeviceTypes, PropertyIDs, DeviceMgmtToggleProps
from wyzeapy.wyze_auth_lib import WyzeAuthLib
import asyncio
from wyzeapy.exceptions import UnknownApiError
from aiohttp import ClientOSError, ContentTypeError


class TestCameraService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        CameraService._updater_thread = None
        CameraService._subscribers = []
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
        self.camera_service._get_iot_prop_devicemgmt = AsyncMock()
        self.camera_service.get_object_list = AsyncMock(
            return_value=[
                MagicMock(type=DeviceTypes.CAMERA, raw_dict={"mac": "CAM1"}),
                MagicMock(type=DeviceTypes.CAMERA, raw_dict={"mac": "CAM2"}),
                MagicMock(type=DeviceTypes.LIGHT, raw_dict={"mac": "BULB1"}),
            ]
        )

        # Create a test camera
        self.test_camera = Camera(
            {
                "device_type": DeviceTypes.CAMERA.value,
                "product_model": "WYZEC1",
                "mac": "TEST123",
                "nickname": "Test Camera",
                "device_params": {"ip": "192.168.1.100"},
                "raw_dict": {},
            }
        )

        self.devicemgmt_camera = Camera(
            {
                "device_type": DeviceTypes.CAMERA.value,
                "product_model": "LD_CFP",  # Floodlight pro model
                "mac": "TEST456",
                "nickname": "Test DeviceMgmt Camera",
                "device_params": {"ip": "192.168.1.101"},
                "raw_dict": {},
            }
        )

        self.bcp_camera = Camera(
            {
                "device_type": DeviceTypes.CAMERA.value,
                "product_model": "AN_RSCW",  # Battery Cam Pro
                "mac": "TEST789",
                "nickname": "Test BCP Camera",
                "device_params": {"ip": "192.168.1.102"},
                "raw_dict": {},
            }
        )

        self.wco2_camera = Camera(
            {
                "device_type": DeviceTypes.CAMERA.value,
                "product_type": DeviceTypes.CAMERA.value,  # Added product_type
                "product_model": "HL_WCO2",  # Wyze Cam Outdoor v2
                "mac": "TEST012",
                "nickname": "Test WCO2 Camera",
                "device_params": {"ip": "192.168.1.103"},
                "raw_dict": {},
            }
        )

    async def test_update_legacy_camera(self):
        # Mock responses
        self.camera_service._get_event_list.return_value = {
            "data": {
                "event_list": [
                    {
                        "event_ts": 1234567890,
                        "device_mac": "TEST123",
                        "event_type": "motion",
                    }
                ]
            }
        }

        self.camera_service._get_property_list.return_value = [
            (PropertyIDs.AVAILABLE, "1"),
            (PropertyIDs.ON, "1"),
            (PropertyIDs.CAMERA_SIREN, "0"),
            (PropertyIDs.ACCESSORY, "0"),
            (PropertyIDs.NOTIFICATION, "1"),
            (PropertyIDs.MOTION_DETECTION, "1"),
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
        self.camera_service._get_iot_prop_devicemgmt.return_value = {
            "data": {
                "capabilities": [
                    {"name": "camera", "properties": {"motion-detect-recording": True}},
                    {"name": "floodlight", "properties": {"on": True}},
                    {"name": "siren", "properties": {"state": True}},
                    {
                        "name": "iot-device",
                        "properties": {
                            "push-switch": True,
                            "iot-power": True,
                            "iot-state": True,
                        },
                    },
                ]
            }
        }

        updated_camera = await self.camera_service.update(self.devicemgmt_camera)

        self.assertTrue(updated_camera.available)
        self.assertTrue(updated_camera.on)
        self.assertTrue(updated_camera.siren)
        self.assertTrue(updated_camera.floodlight)
        self.assertTrue(updated_camera.notify)
        self.assertTrue(updated_camera.motion)

    async def test_turn_on_off_legacy_camera(self):
        await self.camera_service.turn_on(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(
            self.test_camera, "power_on"
        )

        await self.camera_service.turn_off(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(
            self.test_camera, "power_off"
        )

    async def test_turn_on_off_devicemgmt_camera(self):
        await self.camera_service.turn_on(self.devicemgmt_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.devicemgmt_camera, "power", "wakeup"
        )

        await self.camera_service.turn_off(self.devicemgmt_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.devicemgmt_camera, "power", "sleep"
        )

    async def test_siren_control_legacy_camera(self):
        await self.camera_service.siren_on(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(
            self.test_camera, "siren_on"
        )

        await self.camera_service.siren_off(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(
            self.test_camera, "siren_off"
        )

    async def test_siren_control_devicemgmt_camera(self):
        await self.camera_service.siren_on(self.devicemgmt_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.devicemgmt_camera, "siren", "siren-on"
        )

        await self.camera_service.siren_off(self.devicemgmt_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.devicemgmt_camera, "siren", "siren-off"
        )

    async def test_floodlight_control_legacy_camera(self):
        await self.camera_service.floodlight_on(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera, PropertyIDs.ACCESSORY.value, "1"
        )

        await self.camera_service.floodlight_off(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera, PropertyIDs.ACCESSORY.value, "2"
        )

    async def test_floodlight_control_devicemgmt_camera(self):
        await self.camera_service.floodlight_on(self.devicemgmt_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.devicemgmt_camera, "floodlight", "1"
        )

        await self.camera_service.floodlight_off(self.devicemgmt_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.devicemgmt_camera, "floodlight", "0"
        )

    async def test_floodlight_control_bcp_camera(self):
        await self.camera_service.floodlight_on(self.bcp_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.bcp_camera, "spotlight", "1"
        )

        await self.camera_service.floodlight_off(self.bcp_camera)
        self.camera_service._run_action_devicemgmt.assert_awaited_with(
            self.bcp_camera, "spotlight", "0"
        )

    async def test_notification_control_legacy_camera(self):
        await self.camera_service.turn_on_notifications(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera, PropertyIDs.NOTIFICATION.value, "1"
        )

        await self.camera_service.turn_off_notifications(self.test_camera)
        self.camera_service._set_property.assert_awaited_with(
            self.test_camera, PropertyIDs.NOTIFICATION.value, "0"
        )

    async def test_notification_control_devicemgmt_camera(self):
        await self.camera_service.turn_on_notifications(self.devicemgmt_camera)
        self.camera_service._set_toggle.assert_awaited_with(
            self.devicemgmt_camera, DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value, "1"
        )

        await self.camera_service.turn_off_notifications(self.devicemgmt_camera)
        self.camera_service._set_toggle.assert_awaited_with(
            self.devicemgmt_camera, DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value, "0"
        )

    async def test_motion_detection_control_legacy_camera(self):
        await self.camera_service.turn_on_motion_detection(self.test_camera)
        self.camera_service._set_property.assert_any_await(
            self.test_camera, PropertyIDs.MOTION_DETECTION.value, "1"
        )
        self.camera_service._set_property.assert_any_await(
            self.test_camera, PropertyIDs.MOTION_DETECTION_TOGGLE.value, "1"
        )

        await self.camera_service.turn_off_motion_detection(self.test_camera)
        self.camera_service._set_property.assert_any_await(
            self.test_camera, PropertyIDs.MOTION_DETECTION.value, "0"
        )
        self.camera_service._set_property.assert_any_await(
            self.test_camera, PropertyIDs.MOTION_DETECTION_TOGGLE.value, "0"
        )

    async def test_motion_detection_control_devicemgmt_camera(self):
        await self.camera_service.turn_on_motion_detection(self.devicemgmt_camera)
        self.camera_service._set_toggle.assert_awaited_with(
            self.devicemgmt_camera,
            DeviceMgmtToggleProps.EVENT_RECORDING_TOGGLE.value,
            "1",
        )

        await self.camera_service.turn_off_motion_detection(self.devicemgmt_camera)
        self.camera_service._set_toggle.assert_awaited_with(
            self.devicemgmt_camera,
            DeviceMgmtToggleProps.EVENT_RECORDING_TOGGLE.value,
            "0",
        )

    async def test_motion_detection_control_wco2_camera(self):
        with patch(
            "wyzeapy.services.camera_service.create_pid_pair",
            side_effect=lambda x, y: (x, y),
        ):
            await self.camera_service.turn_on_motion_detection(self.wco2_camera)
            self.camera_service._set_property_list.assert_awaited_with(
                self.wco2_camera, [(PropertyIDs.WCO_MOTION_DETECTION, "1")]
            )

            await self.camera_service.turn_off_motion_detection(self.wco2_camera)
            self.camera_service._set_property_list.assert_awaited_with(
                self.wco2_camera, [(PropertyIDs.WCO_MOTION_DETECTION, "0")]
            )

    async def test_garage_door_open_close(self):
        await self.camera_service.garage_door_open(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(
            self.test_camera, "garage_door_trigger"
        )

        await self.camera_service.garage_door_close(self.test_camera)
        self.camera_service._run_action.assert_awaited_with(
            self.test_camera, "garage_door_trigger"
        )

    async def test_get_cameras(self):
        self.camera_service.get_object_list.return_value = [
            MagicMock(type=DeviceTypes.CAMERA, raw_dict={"mac": "CAM1"}),
            MagicMock(type=DeviceTypes.CAMERA, raw_dict={"mac": "CAM2"}),
            MagicMock(type=DeviceTypes.LIGHT, raw_dict={"mac": "BULB1"}),
        ]
        cameras = await self.camera_service.get_cameras()
        self.assertEqual(len(cameras), 2)
        self.assertIsInstance(cameras[0], Camera)
        self.assertEqual(cameras[0].mac, "CAM1")
        self.assertEqual(cameras[1].mac, "CAM2")

    async def test_register_for_updates(self):
        mock_callback = MagicMock()
        await self.camera_service.register_for_updates(self.test_camera, mock_callback)
        self.assertEqual(len(self.camera_service._subscribers), 1)
        self.assertEqual(self.camera_service._subscribers[0][0], self.test_camera)
        self.assertEqual(self.camera_service._subscribers[0][1], mock_callback)
        self.assertIsNotNone(self.camera_service._updater_thread)
        self.assertTrue(self.camera_service._updater_thread.is_alive())

    async def test_deregister_for_updates(self):
        mock_callback1 = MagicMock()
        mock_callback2 = MagicMock()
        camera2 = Camera({"mac": "TEST999"})
        await self.camera_service.register_for_updates(self.test_camera, mock_callback1)
        await self.camera_service.register_for_updates(camera2, mock_callback2)
        self.assertEqual(len(self.camera_service._subscribers), 2)

        await self.camera_service.deregister_for_updates(self.test_camera)
        self.assertEqual(len(self.camera_service._subscribers), 1)
        self.assertEqual(self.camera_service._subscribers[0][0], camera2)

    async def test_update_worker_success(self):
        mock_callback = MagicMock()
        mock_callback.return_value = None  # Ensure callback doesn't return a coroutine
        self.camera_service.update = AsyncMock(return_value=self.test_camera)

        await self.camera_service.register_for_updates(self.test_camera, mock_callback)

        # Give the worker a moment to run
        await asyncio.sleep(0.2)

        # Manually stop the thread for testing purposes
        self.camera_service._subscribers = []
        self.camera_service._updater_thread.join(timeout=1)

        # The update method should have been called at least once
        self.assertGreater(self.camera_service.update.call_count, 0)
        # The callback should have been called at least once
        self.assertGreater(mock_callback.call_count, 0)

    async def test_update_worker_exceptions(self):
        mock_callback = MagicMock()

        # Create a series of exceptions that will be raised when update is called
        exceptions_to_raise = [
            UnknownApiError("API Error"),
            ClientOSError(),
            ContentTypeError(
                request_info=MagicMock(), history=(), status=200, message=""
            ),
        ]

        self.camera_service.update = AsyncMock(side_effect=exceptions_to_raise)

        with (
            patch("wyzeapy.services.camera_service._LOGGER.warning") as mock_warning,
            patch("wyzeapy.services.camera_service._LOGGER.error") as mock_error,
        ):
            await self.camera_service.register_for_updates(
                self.test_camera, mock_callback
            )

            # Give the worker a moment to run through exceptions
            await asyncio.sleep(0.3)

            # Manually stop the thread for testing purposes
            self.camera_service._subscribers = []
            self.camera_service._updater_thread.join(timeout=1)

            # Check that the update method was called at least the number of exceptions we set up
            self.assertGreaterEqual(
                self.camera_service.update.call_count, len(exceptions_to_raise)
            )
            # Check that the warning was called for UnknownApiError
            mock_warning.assert_called_with(
                "The update method detected an UnknownApiError: API Error"
            )
            # Check that error was called for other exceptions
            self.assertGreaterEqual(mock_error.call_count, 2)


if __name__ == "__main__":
    unittest.main()
