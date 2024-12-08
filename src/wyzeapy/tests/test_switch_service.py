import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.switch_service import SwitchService, SwitchUsageService, Switch
from wyzeapy.types import DeviceTypes, PropertyIDs
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestSwitchService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.switch_service = SwitchService(auth_lib=self.mock_auth_lib)
        self.switch_service._get_property_list = AsyncMock()
        self.switch_service.get_updated_params = AsyncMock()
        self.switch_service.get_object_list = AsyncMock()
        self.switch_service._set_property = AsyncMock()

        # Create test switch
        self.test_switch = Switch({
            "device_type": DeviceTypes.PLUG.value,
            "product_model": "WLPP1",
            "mac": "SWITCH123",
            "nickname": "Test Switch",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_switch_on(self):
        self.switch_service._get_property_list.return_value = [
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1")
        ]

        updated_switch = await self.switch_service.update(self.test_switch)
        
        self.assertTrue(updated_switch.on)
        self.assertTrue(updated_switch.available)

    async def test_update_switch_off(self):
        self.switch_service._get_property_list.return_value = [
            (PropertyIDs.ON, "0"),
            (PropertyIDs.AVAILABLE, "1")
        ]

        updated_switch = await self.switch_service.update(self.test_switch)
        
        self.assertFalse(updated_switch.on)
        self.assertTrue(updated_switch.available)

    async def test_get_switches(self):
        mock_plug = MagicMock()
        mock_plug.type = DeviceTypes.PLUG
        mock_plug.raw_dict = {
            "device_type": DeviceTypes.PLUG.value,
            "product_model": "WLPP1",
            "mac": "PLUG123"
        }

        mock_outdoor_plug = MagicMock()
        mock_outdoor_plug.type = DeviceTypes.OUTDOOR_PLUG
        mock_outdoor_plug.raw_dict = {
            "device_type": DeviceTypes.OUTDOOR_PLUG.value,
            "product_model": "WLPPO",
            "mac": "OUTPLUG456"
        }

        self.switch_service.get_object_list.return_value = [
            mock_plug,
            mock_outdoor_plug
        ]

        switches = await self.switch_service.get_switches()
        
        self.assertEqual(len(switches), 2)
        self.assertIsInstance(switches[0], Switch)
        self.assertIsInstance(switches[1], Switch)
        self.switch_service.get_object_list.assert_awaited_once()

    async def test_turn_on(self):
        await self.switch_service.turn_on(self.test_switch)
        self.switch_service._set_property.assert_awaited_with(
            self.test_switch,
            PropertyIDs.ON.value,
            "1"
        )

    async def test_turn_off(self):
        await self.switch_service.turn_off(self.test_switch)
        self.switch_service._set_property.assert_awaited_with(
            self.test_switch,
            PropertyIDs.ON.value,
            "0"
        )


class TestSwitchUsageService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.usage_service = SwitchUsageService(auth_lib=self.mock_auth_lib)
        self.usage_service._get_plug_history = AsyncMock()

        # Create test switch
        self.test_switch = Switch({
            "device_type": DeviceTypes.PLUG.value,
            "product_model": "WLPP1",
            "mac": "SWITCH123",
            "nickname": "Test Switch",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_usage_history(self):
        mock_usage_data = {
            "total_power": 100,
            "time_series": [
                {"power": 10, "timestamp": 1234567890},
                {"power": 20, "timestamp": 1234567891}
            ]
        }
        self.usage_service._get_plug_history.return_value = mock_usage_data

        # Calculate expected timestamps
        now = datetime.now()
        expected_end_time = int(datetime.timestamp(now) * 1000)
        expected_start_time = int(datetime.timestamp(now - timedelta(hours=25)) * 1000)

        updated_switch = await self.usage_service.update(self.test_switch)

        self.assertEqual(updated_switch.usage_history, mock_usage_data)
        self.usage_service._get_plug_history.assert_awaited_with(
            self.test_switch,
            expected_start_time,
            expected_end_time
        )


if __name__ == '__main__':
    unittest.main() 