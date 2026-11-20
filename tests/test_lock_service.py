import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.lock_service import LockService, Lock
from wyzeapy.types import DeviceTypes
from wyzeapy.exceptions import UnknownApiError
import urllib.parse

# Mock urllib.parse.quote_plus to return a string
urllib.parse.quote_plus = MagicMock(return_value="mocked_quoted_string")


class TestLockService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        mock_auth_lib = AsyncMock()
        mock_auth_lib.refresh_if_should = AsyncMock()
        self.lock_service = LockService(auth_lib=mock_auth_lib)
        self.lock_service._get_lock_info = AsyncMock()
        self.lock_service._lock_control = AsyncMock()
        self.lock_service._auth_lib.get.return_value = {
            "ErrNo": 0,
            "token": {"id": "mock_id", "token": "0123456789abcdef0123456789abcdef"},
        }

    async def test_update_lock_online(self):
        mock_lock = Lock(
            {
                "device_type": "Lock",
                "mac": "test_mac_online",
                "onoff_line": 1,
                "door_open_status": 0,
                "trash_mode": 0,
                "locker_status": {"hardlock": 2},
                "raw_dict": {},
            }
        )
        mock_lock.product_model = "YD_BT1"
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
        mock_lock = Lock(
            {
                "device_type": "Lock",
                "mac": "test_mac_offline",
                "onoff_line": 0,
                "door_open_status": 1,
                "trash_mode": 1,
                "locker_status": {"hardlock": 1},
                "raw_dict": {},
            }
        )
        mock_lock.product_model = "YD_BT1"
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
        mock_lock = Lock({"device_type": "Lock", "raw_dict": {}})

        await self.lock_service.lock(mock_lock)
        self.lock_service._lock_control.assert_awaited_with(mock_lock, "remoteLock")

    async def test_unlock(self):
        mock_lock = Lock({"device_type": "Lock", "raw_dict": {}})

        await self.lock_service.unlock(mock_lock)
        self.lock_service._lock_control.assert_awaited_with(mock_lock, "remoteUnlock")

    async def test_lock_control_error_handling(self):
        mock_lock = Lock({"device_type": "Lock", "raw_dict": {}})
        self.lock_service._lock_control.side_effect = UnknownApiError(
            "Failed to lock/unlock"
        )

        with self.assertRaises(UnknownApiError):
            await self.lock_service.lock(mock_lock)

        with self.assertRaises(UnknownApiError):
            await self.lock_service.unlock(mock_lock)

    async def test_update_iot3_lock(self):
        mock_lock = Lock(
            {
                "device_type": "Common",
                "product_model": "DX_PVLOC",
                "mac": "DX_PVLOC_abc123",
                "raw_dict": {},
            }
        )
        self.lock_service._auth_lib.post.return_value = {
            "code": "1",
            "data": {
                "props": {
                    "lock::lock-status": True,
                    "battery::battery-level": 97,
                    "iot-device::iot-state": True,
                }
            },
        }

        updated_lock = await self.lock_service.update(mock_lock)

        self.assertTrue(updated_lock.available)
        # lock-status True means the lock is physically LOCKED, so it must
        # be inverted to get this module's `unlocked` convention.
        self.assertFalse(updated_lock.unlocked)
        self.assertEqual(updated_lock.raw_dict["power"], 97)
        self.lock_service._get_lock_info.assert_not_awaited()

    async def test_get_locks_includes_iot3_models(self):
        mock_regular_lock = AsyncMock()
        mock_regular_lock.type = DeviceTypes.LOCK
        mock_regular_lock.product_model = "YD_BT1"
        mock_regular_lock.raw_dict = {"device_type": "Lock"}

        mock_palm_lock = AsyncMock()
        mock_palm_lock.type = DeviceTypes.UNKNOWN
        mock_palm_lock.product_model = "DX_PVLOC"
        mock_palm_lock.raw_dict = {"device_type": "Common", "product_model": "DX_PVLOC"}

        self.lock_service.get_object_list = AsyncMock(
            return_value=[mock_regular_lock, mock_palm_lock]
        )

        locks = await self.lock_service.get_locks()

        self.assertEqual(len(locks), 2)
        self.assertTrue(all(isinstance(lock, Lock) for lock in locks))

    async def test_lock_unlock_iot3(self):
        mock_lock = Lock(
            {
                "device_type": "Common",
                "product_model": "DX_PVLOC",
                "mac": "DX_PVLOC_abc123",
                "raw_dict": {},
            }
        )
        self.lock_service._auth_lib.post.return_value = {"code": "1"}
        self.lock_service._auth_lib._username = "test_user"

        await self.lock_service.lock(mock_lock)
        await self.lock_service.unlock(mock_lock)

        self.lock_service._lock_control.assert_not_awaited()
        self.assertEqual(self.lock_service._auth_lib.post.await_count, 2)
