import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.lock_service import LockService, Lock
from wyzeapy.types import DeviceTypes
from wyzeapy.exceptions import UnknownApiError

class TestLockService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        mock_auth_lib = MagicMock()
        self.lock_service = LockService(auth_lib=mock_auth_lib)
        self.lock_service._get_lock_info = AsyncMock()
        self.lock_service._lock_control = AsyncMock()

    async def test_update_lock_online(self):
        mock_lock = Lock({
            "device_type": "Lock",
            "onoff_line": 1,
            "door_open_status": 0,
            "trash_mode": 0,
            "locker_status": {"hardlock": 2},
            "raw_dict": {}
        })
        self.lock_service._get_lock_info.return_value = {
            "device": {
                "onoff_line": 1,
                "door_open_status": 0,
                "trash_mode": 0,
                "locker_status": {"hardlock": 2},
            }
        }

        updated_lock = await self.lock_service.update(mock_lock)

        self.assertTrue(updated_lock.available)
        self.assertFalse(updated_lock.door_open)
        self.assertFalse(updated_lock.trash_mode)
        self.assertTrue(updated_lock.unlocked)
        self.assertFalse(updated_lock.unlocking)
        self.assertFalse(updated_lock.locking)
        self.lock_service._get_lock_info.assert_awaited_once_with(mock_lock)

    async def test_update_lock_offline(self):
        mock_lock = Lock({
            "device_type": "Lock",
            "onoff_line": 0,
            "door_open_status": 1,
            "trash_mode": 1,
            "locker_status": {"hardlock": 1},
            "raw_dict": {}
        })
        self.lock_service._get_lock_info.return_value = {
            "device": {
                "onoff_line": 0,
                "door_open_status": 1,
                "trash_mode": 1,
                "locker_status": {"hardlock": 1},
            }
        }

        updated_lock = await self.lock_service.update(mock_lock)

        self.assertFalse(updated_lock.available)
        self.assertTrue(updated_lock.door_open)
        self.assertTrue(updated_lock.trash_mode)
        self.assertFalse(updated_lock.unlocked)
        self.assertFalse(updated_lock.unlocking)
        self.assertFalse(updated_lock.locking)
        self.lock_service._get_lock_info.assert_awaited_once_with(mock_lock)

    async def test_get_locks(self):
        mock_device = AsyncMock()
        mock_device.type = DeviceTypes.LOCK
        mock_device.raw_dict = {"device_type": "Lock"}

        self.lock_service.get_object_list = AsyncMock(return_value=[mock_device])

        locks = await self.lock_service.get_locks()

        self.assertEqual(len(locks), 1)
        self.assertIsInstance(locks[0], Lock)
        self.lock_service.get_object_list.assert_awaited_once()

    async def test_lock(self):
        mock_lock = Lock({
            "device_type": "Lock",
            "raw_dict": {}
        })

        await self.lock_service.lock(mock_lock)
        self.lock_service._lock_control.assert_awaited_with(mock_lock, "remoteLock")

    async def test_unlock(self):
        mock_lock = Lock({
            "device_type": "Lock",
            "raw_dict": {}
        })

        await self.lock_service.unlock(mock_lock)
        self.lock_service._lock_control.assert_awaited_with(mock_lock, "remoteUnlock")

    async def test_lock_control_error_handling(self):
        mock_lock = Lock({
            "device_type": "Lock",
            "raw_dict": {}
        })
        self.lock_service._lock_control.side_effect = UnknownApiError("Failed to lock/unlock")

        with self.assertRaises(UnknownApiError):
            await self.lock_service.lock(mock_lock)

        with self.assertRaises(UnknownApiError):
            await self.lock_service.unlock(mock_lock)

# ... other test cases ... 