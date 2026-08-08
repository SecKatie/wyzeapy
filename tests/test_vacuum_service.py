import unittest
from unittest.mock import AsyncMock, MagicMock

from wyzeapy.exceptions import UnknownApiError
from wyzeapy.services.vacuum_service import (
    Vacuum,
    VacuumFaultCode,
    VacuumMode,
    VacuumService,
    VacuumSuctionLevel,
)
from wyzeapy.types import DeviceTypes
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestVacuumMode(unittest.TestCase):
    def test_parse_maps_every_documented_code(self):
        self.assertIs(VacuumMode.parse(0), VacuumMode.IDLE)
        self.assertIs(VacuumMode.parse(1), VacuumMode.CLEANING)
        self.assertIs(VacuumMode.parse(1301), VacuumMode.CLEANING)
        self.assertIs(VacuumMode.parse(4), VacuumMode.PAUSED)
        self.assertIs(VacuumMode.parse(5), VacuumMode.RETURNING_TO_CHARGE)
        self.assertIs(VacuumMode.parse(10), VacuumMode.FINISHED_RETURNING_TO_CHARGE)
        self.assertIs(VacuumMode.parse(11), VacuumMode.DOCKED_NOT_COMPLETE)
        self.assertIs(VacuumMode.parse(45), VacuumMode.MAPPING)

    def test_parse_accepts_a_string_code(self):
        self.assertIs(VacuumMode.parse("5"), VacuumMode.RETURNING_TO_CHARGE)

    def test_parse_returns_unknown_for_an_unlisted_code(self):
        self.assertIs(VacuumMode.parse(9999), VacuumMode.UNKNOWN)
        self.assertIs(VacuumMode.parse(None), VacuumMode.UNKNOWN)


class TestVacuumFaultCode(unittest.TestCase):
    def test_parse_maps_a_known_fault(self):
        self.assertIs(VacuumFaultCode.parse(510), VacuumFaultCode.COLLISION_EXCEPTION)
        self.assertIs(VacuumFaultCode.parse("510"), VacuumFaultCode.COLLISION_EXCEPTION)

    def test_an_undocumented_code_is_not_a_fault(self):
        """A healthy docked vacuum reports 2105 steadily; non-zero is not a fault."""
        self.assertIsNone(VacuumFaultCode.parse(2105))
        self.assertIsNone(VacuumFaultCode.parse(0))
        self.assertIsNone(VacuumFaultCode.parse(None))


class TestVacuumService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.vacuum_service = VacuumService(auth_lib=self.mock_auth_lib)
        self.vacuum_service._get_iot_prop = AsyncMock()
        self.vacuum_service._venus_control = AsyncMock()
        self.vacuum_service._venus_set_iot_action = AsyncMock()
        self.vacuum_service.get_object_list = AsyncMock()

        self.test_vacuum = Vacuum(
            {
                "product_type": DeviceTypes.VACUUM.value,
                "product_model": "JA_RO2",
                "mac": "JA_RO2_ABCDEF1234567890",
                "nickname": "Test Vacuum",
                "device_params": {},
                "raw_dict": {},
            }
        )

    async def test_update_reads_every_prop(self):
        self.vacuum_service._get_iot_prop.return_value = {
            "data": {
                "props": {
                    "iot_state": "connected",
                    "battary": 87,
                    "mode": 1,
                    "chargeState": 0,
                    "cleanSize": 12,
                    "cleanTime": 34,
                    "cleanlevel": 3,
                    "fault_code": 0,
                    "current_mapid": 1738263642,
                    "filter": 461,
                    "side_brush": 445,
                    "main_brush": 461,
                }
            }
        }

        vacuum = await self.vacuum_service.update(self.test_vacuum)

        self.assertTrue(vacuum.available)
        self.assertEqual(vacuum.battery, 87)
        self.assertIs(vacuum.mode, VacuumMode.CLEANING)
        self.assertFalse(vacuum.charging)
        self.assertEqual(vacuum.clean_size, 12)
        self.assertEqual(vacuum.clean_time, 34)
        self.assertIs(vacuum.suction_level, VacuumSuctionLevel.STRONG)
        self.assertEqual(vacuum.fault_code, 0)
        self.assertIsNone(vacuum.fault)
        self.assertEqual(vacuum.current_map_id, 1738263642)
        self.assertEqual(vacuum.filter_remaining, 461)
        self.assertEqual(vacuum.side_brush_remaining, 445)
        self.assertEqual(vacuum.main_brush_remaining, 461)

    async def test_update_marks_a_disconnected_vacuum_unavailable(self):
        self.vacuum_service._get_iot_prop.return_value = {
            "data": {"props": {"iot_state": "disconnected", "battary": 100, "mode": 0}}
        }

        vacuum = await self.vacuum_service.update(self.test_vacuum)

        self.assertFalse(vacuum.available)
        self.assertIs(vacuum.mode, VacuumMode.IDLE)

    async def test_a_disconnected_vacuum_is_unavailable_even_though_reads_work(self):
        """Sleep leaves the cloud readable but not commandable, so both must be true.

        Guards the pairing that makes availability correct rather than over-strict:
        a live JA_RO2 asleep on its dock answers a read in full and refuses every
        command with code 3000 "Device is offline". Anyone tempted to let
        `available` follow whether venus answered should have this fail.
        """
        self.vacuum_service._get_iot_prop.return_value = {
            "data": {
                "props": {
                    "iot_state": "disconnected",
                    "battary": 100,
                    "mode": 0,
                    "chargeState": 1,
                }
            }
        }
        self.vacuum_service._venus_control.side_effect = UnknownApiError(
            {"code": 3000, "message": "Device is offline", "data": None}
        )

        vacuum = await self.vacuum_service.update(self.test_vacuum)

        self.assertFalse(vacuum.available)
        self.assertEqual(vacuum.battery, 100)
        self.assertTrue(vacuum.charging)
        with self.assertRaises(UnknownApiError):
            await self.vacuum_service.sweep(vacuum)

    async def test_update_survives_a_partial_prop_payload(self):
        """The API omits props it has no value for; an absent key must not wipe state."""
        self.test_vacuum.battery = 42
        self.vacuum_service._get_iot_prop.return_value = {"data": {"props": {}}}

        vacuum = await self.vacuum_service.update(self.test_vacuum)

        self.assertEqual(vacuum.battery, 42)

    async def test_update_ignores_an_unparsable_value(self):
        self.vacuum_service._get_iot_prop.return_value = {
            "data": {"props": {"battary": "not-a-number", "mode": 0}}
        }

        vacuum = await self.vacuum_service.update(self.test_vacuum)

        self.assertIsNone(vacuum.battery)

    async def test_get_vacuums_filters_by_device_type(self):
        matching = MagicMock()
        matching.type = DeviceTypes.VACUUM
        matching.raw_dict = {
            "product_type": DeviceTypes.VACUUM.value,
            "product_model": "JA_RO2",
            "mac": "JA_RO2_ABCDEF1234567890",
            "nickname": "Test Vacuum",
        }
        other = MagicMock()
        other.type = DeviceTypes.CAMERA
        self.vacuum_service.get_object_list.return_value = [matching, other]

        vacuums = await self.vacuum_service.get_vacuums()

        self.assertEqual(len(vacuums), 1)
        self.assertEqual(vacuums[0].nickname, "Test Vacuum")

    async def test_sweep_starts_a_global_sweep(self):
        await self.vacuum_service.sweep(self.test_vacuum)

        self.vacuum_service._venus_control.assert_awaited_once_with(
            self.test_vacuum, 0, 1
        )

    async def test_pause_pauses_the_global_sweep(self):
        await self.vacuum_service.pause(self.test_vacuum)

        self.vacuum_service._venus_control.assert_awaited_once_with(
            self.test_vacuum, 0, 2
        )

    async def test_return_to_charge_docks_the_vacuum(self):
        await self.vacuum_service.return_to_charge(self.test_vacuum)

        self.vacuum_service._venus_control.assert_awaited_once_with(
            self.test_vacuum, 3, 1
        )

    async def test_stop_cancels_the_return_to_charge(self):
        await self.vacuum_service.stop(self.test_vacuum)

        self.vacuum_service._venus_control.assert_awaited_once_with(
            self.test_vacuum, 3, 0
        )

    async def test_set_suction_level_sends_the_preference(self):
        await self.vacuum_service.set_suction_level(
            self.test_vacuum, VacuumSuctionLevel.QUIET
        )

        self.vacuum_service._venus_set_iot_action.assert_awaited_once_with(
            self.test_vacuum, "set_preference", {"ctrltype": 1, "value": 1}
        )

    async def test_set_suction_level_accepts_the_level_by_name(self):
        await self.vacuum_service.set_suction_level(self.test_vacuum, "Strong")

        self.vacuum_service._venus_set_iot_action.assert_awaited_once_with(
            self.test_vacuum, "set_preference", {"ctrltype": 1, "value": 3}
        )

    async def test_set_suction_level_rejects_an_unknown_level(self):
        with self.assertRaises(ValueError):
            await self.vacuum_service.set_suction_level(self.test_vacuum, "Turbo")

        self.vacuum_service._venus_set_iot_action.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
