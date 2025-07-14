import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from wyzeapy.services.update_manager import DeviceUpdater, UpdateManager, MAX_SLOTS
from wyzeapy.types import Device


class TestDeviceUpdater(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_service = MagicMock()
        self.mock_device = MagicMock(spec=Device)
        self.mock_device.nickname = "TestDevice"
        self.mock_device.callback_function = AsyncMock()

    def test_init(self):
        updater = DeviceUpdater(self.mock_service, self.mock_device, 60)
        self.assertEqual(updater.service, self.mock_service)
        self.assertEqual(updater.device, self.mock_device)
        self.assertEqual(updater.update_in, 0)
        self.assertEqual(updater.updates_per_interval, 5)  # ceil(300/60)

    async def test_update_when_ready(self):
        updater = DeviceUpdater(self.mock_service, self.mock_device, 60)
        updater.update_in = 0
        self.mock_service.update = AsyncMock(return_value=self.mock_device)
        mock_mutex = MagicMock()
        mock_mutex.acquire = MagicMock()
        mock_mutex.release = MagicMock()

        await updater.update(mock_mutex)

        self.mock_service.update.assert_awaited_once_with(self.mock_device)
        self.mock_device.callback_function.assert_called_once_with(self.mock_device)
        mock_mutex.acquire.assert_called_once()
        mock_mutex.release.assert_called_once()
        self.assertEqual(
            updater.update_in, 60
        )  # Reset to ceil(INTERVAL / updates_per_interval)

    async def test_update_when_not_ready(self):
        updater = DeviceUpdater(self.mock_service, self.mock_device, 60)
        updater.update_in = 3
        self.mock_service.update = AsyncMock()
        mock_mutex = MagicMock()
        mock_mutex.acquire = MagicMock()
        mock_mutex.release = MagicMock()

        await updater.update(mock_mutex)

        self.mock_service.update.assert_not_awaited()
        self.mock_device.callback_function.assert_not_called()
        mock_mutex.acquire.assert_not_called()
        mock_mutex.release.assert_not_called()
        self.assertEqual(updater.update_in, 2)  # update_in reduced by 1

    async def test_update_exception_handling(self):
        updater = DeviceUpdater(self.mock_service, self.mock_device, 60)
        updater.update_in = 0
        self.mock_service.update = AsyncMock(side_effect=Exception("Test Exception"))
        mock_mutex = MagicMock()
        mock_mutex.acquire = MagicMock()
        mock_mutex.release = MagicMock()

        await updater.update(mock_mutex)

        self.mock_service.update.assert_awaited_once_with(self.mock_device)
        self.mock_device.callback_function.assert_not_called()
        mock_mutex.acquire.assert_called_once()
        mock_mutex.release.assert_called_once()
        self.assertEqual(updater.update_in, 60)  # Still resets update_in

    def test_tick_tock(self):
        updater = DeviceUpdater(self.mock_service, self.mock_device, 60)
        updater.update_in = 5
        updater.tick_tock()
        self.assertEqual(updater.update_in, 4)

        updater.update_in = 0
        updater.tick_tock()
        self.assertEqual(updater.update_in, 0)  # Should not go below 0

    def test_delay(self):
        updater = DeviceUpdater(self.mock_service, self.mock_device, 60)
        updater.updates_per_interval = 5
        updater.delay()
        self.assertEqual(updater.updates_per_interval, 4)

        updater.updates_per_interval = 1
        updater.delay()
        self.assertEqual(updater.updates_per_interval, 1)  # Should not go below 1


class TestUpdateManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Reset the class-level attributes before each test
        UpdateManager.updaters = []
        UpdateManager.removed_updaters = []
        self.update_manager = UpdateManager()
        # For logging assertions
        import logging

        self.caplog = logging.getLogger("wyzeapy.services.update_manager")
        self.caplog.setLevel(logging.DEBUG)

    def test_check_if_removed(self):
        mock_updater1 = MagicMock()
        mock_updater2 = MagicMock()
        self.update_manager.removed_updaters.append(mock_updater1)

        self.assertTrue(self.update_manager.check_if_removed(mock_updater1))
        self.assertFalse(self.update_manager.check_if_removed(mock_updater2))

    @patch("asyncio.sleep", new_callable=AsyncMock)
    async def test_update_next_no_updaters(self, mock_sleep):
        with self.assertLogs("wyzeapy.services.update_manager", level="DEBUG") as cm:
            await self.update_manager.update_next()
            self.assertIn("No devices to update in queue", cm.output[0])
        mock_sleep.assert_not_awaited()

    def test_filled_slots(self):
        updater1 = DeviceUpdater(
            MagicMock(), MagicMock(), 60
        )  # updates_per_interval = 5
        updater2 = DeviceUpdater(
            MagicMock(), MagicMock(), 150
        )  # updates_per_interval = 2
        self.update_manager.updaters.extend([updater1, updater2])
        self.assertEqual(self.update_manager.filled_slots(), 7)

    def test_decrease_updates_per_interval(self):
        updater1 = DeviceUpdater(
            MagicMock(), MagicMock(), 60
        )  # updates_per_interval = 5
        updater2 = DeviceUpdater(
            MagicMock(), MagicMock(), 150
        )  # updates_per_interval = 2
        self.update_manager.updaters.extend([updater1, updater2])

        self.update_manager.decrease_updates_per_interval()
        self.assertEqual(updater1.updates_per_interval, 4)
        self.assertEqual(updater2.updates_per_interval, 1)

    def test_tick_tock_manager(self):
        updater1 = DeviceUpdater(MagicMock(), MagicMock(), 60)
        updater1.update_in = 5
        updater2 = DeviceUpdater(MagicMock(), MagicMock(), 150)
        updater2.update_in = 2
        self.update_manager.updaters.extend([updater1, updater2])

        self.update_manager.tick_tock()
        self.assertEqual(updater1.update_in, 4)
        self.assertEqual(updater2.update_in, 1)

    def test_add_updater_success(self):
        updater = DeviceUpdater(
            MagicMock(), MagicMock(), 60
        )  # updates_per_interval = 5
        self.update_manager.add_updater(updater)
        self.assertIn(updater, self.update_manager.updaters)
        self.assertEqual(self.update_manager.filled_slots(), 5)

    def test_add_updater_exceeds_max_slots(self):
        # Directly set updaters to exceed MAX_SLOTS
        UpdateManager.updaters = [MagicMock()] * (MAX_SLOTS + 1)

        new_updater = DeviceUpdater(
            MagicMock(), MagicMock(), 1
        )  # updates_per_interval = 300

        with self.assertRaises(Exception) as cm:
            self.update_manager.add_updater(new_updater)
        self.assertIn(
            "No more devices can be updated within the rate limit", str(cm.exception)
        )

    def test_add_updater_reduces_frequency(self):
        # Add updaters that will cause overflow, forcing frequency reduction
        updater1 = DeviceUpdater(MagicMock(), MagicMock(), 1)  # 300 updates/interval
        updater2 = DeviceUpdater(MagicMock(), MagicMock(), 1)  # 300 updates/interval
        updater3 = DeviceUpdater(MagicMock(), MagicMock(), 1)  # 300 updates/interval

        # Set MAX_SLOTS to a small number for easier testing of overflow
        with patch("wyzeapy.services.update_manager.MAX_SLOTS", 500):
            self.update_manager.add_updater(updater1)
            self.update_manager.add_updater(updater2)
            self.update_manager.add_updater(updater3)

            # Check that updates_per_interval has been reduced for existing updaters
            self.assertLess(updater1.updates_per_interval, 300)
            self.assertLess(updater2.updates_per_interval, 300)
            self.assertLess(updater3.updates_per_interval, 300)

    def test_del_updater(self):
        updater = DeviceUpdater(MagicMock(), MagicMock(), 60)
        self.update_manager.updaters.append(updater)
        self.assertIn(updater, self.update_manager.updaters)

        with self.assertLogs("wyzeapy.services.update_manager", level="DEBUG") as cm:
            self.update_manager.del_updater(updater)
            self.assertIn("Removing device from update queue", cm.output[0])
