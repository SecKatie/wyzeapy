import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.wall_switch_service import (
    WallSwitchService, WallSwitch, SinglePressType, WallSwitchProps
)
from wyzeapy.types import DeviceTypes
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestWallSwitchService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.wall_switch_service = WallSwitchService(auth_lib=self.mock_auth_lib)
        self.wall_switch_service._wall_switch_get_iot_prop = AsyncMock()
        self.wall_switch_service._wall_switch_set_iot_prop = AsyncMock()
        self.wall_switch_service.get_object_list = AsyncMock()

        # Create test wall switch
        self.test_switch = WallSwitch({
            "device_type": DeviceTypes.COMMON.value,
            "product_model": "LD_SS1",
            "mac": "SWITCH123",
            "nickname": "Test Wall Switch",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_wall_switch(self):
        self.wall_switch_service._wall_switch_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'iot_state': 'connected',
                    'switch-power': True,
                    'switch-iot': False,
                    'single_press_type': 1
                }
            }
        }

        updated_switch = await self.wall_switch_service.update(self.test_switch)

        self.assertTrue(updated_switch.available)
        self.assertTrue(updated_switch.switch_power)
        self.assertFalse(updated_switch.switch_iot)
        self.assertEqual(updated_switch.single_press_type, SinglePressType.CLASSIC)
        # Test the property that depends on single_press_type
        self.assertTrue(updated_switch.on)  # Should be True because switch_power is True and type is CLASSIC

    async def test_update_wall_switch_iot_mode(self):
        self.wall_switch_service._wall_switch_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'iot_state': 'connected',
                    'switch-power': False,
                    'switch-iot': True,
                    'single_press_type': 2
                }
            }
        }

        updated_switch = await self.wall_switch_service.update(self.test_switch)

        self.assertTrue(updated_switch.available)
        self.assertFalse(updated_switch.switch_power)
        self.assertTrue(updated_switch.switch_iot)
        self.assertEqual(updated_switch.single_press_type, SinglePressType.IOT)
        # Test the property that depends on single_press_type
        self.assertTrue(updated_switch.on)  # Should be True because switch_iot is True and type is IOT

    async def test_get_switches(self):
        mock_switch = MagicMock()
        mock_switch.type = DeviceTypes.COMMON
        mock_switch.product_model = "LD_SS1"
        mock_switch.raw_dict = {
            "device_type": DeviceTypes.COMMON.value,
            "product_model": "LD_SS1",
            "mac": "SWITCH123"
        }

        # Add a non-wall switch device to test filtering
        mock_other_device = MagicMock()
        mock_other_device.type = DeviceTypes.COMMON
        mock_other_device.product_model = "OTHER_MODEL"

        self.wall_switch_service.get_object_list.return_value = [
            mock_switch,
            mock_other_device
        ]

        switches = await self.wall_switch_service.get_switches()
        
        self.assertEqual(len(switches), 1)
        self.assertIsInstance(switches[0], WallSwitch)
        self.wall_switch_service.get_object_list.assert_awaited_once()

    async def test_turn_on_classic_mode(self):
        self.test_switch.single_press_type = SinglePressType.CLASSIC
        await self.wall_switch_service.turn_on(self.test_switch)
        self.wall_switch_service._wall_switch_set_iot_prop.assert_awaited_with(
            self.test_switch,
            WallSwitchProps.SWITCH_POWER,
            True
        )

    async def test_turn_off_classic_mode(self):
        self.test_switch.single_press_type = SinglePressType.CLASSIC
        await self.wall_switch_service.turn_off(self.test_switch)
        self.wall_switch_service._wall_switch_set_iot_prop.assert_awaited_with(
            self.test_switch,
            WallSwitchProps.SWITCH_POWER,
            False
        )

    async def test_turn_on_iot_mode(self):
        self.test_switch.single_press_type = SinglePressType.IOT
        await self.wall_switch_service.turn_on(self.test_switch)
        self.wall_switch_service._wall_switch_set_iot_prop.assert_awaited_with(
            self.test_switch,
            WallSwitchProps.SWITCH_IOT,
            True
        )

    async def test_turn_off_iot_mode(self):
        self.test_switch.single_press_type = SinglePressType.IOT
        await self.wall_switch_service.turn_off(self.test_switch)
        self.wall_switch_service._wall_switch_set_iot_prop.assert_awaited_with(
            self.test_switch,
            WallSwitchProps.SWITCH_IOT,
            False
        )

    async def test_set_single_press_type(self):
        await self.wall_switch_service.set_single_press_type(
            self.test_switch,
            SinglePressType.IOT
        )
        self.wall_switch_service._wall_switch_set_iot_prop.assert_awaited_with(
            self.test_switch,
            WallSwitchProps.SINGLE_PRESS_TYPE,
            SinglePressType.IOT.value
        )

    async def test_update_with_invalid_property(self):
        self.wall_switch_service._wall_switch_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'invalid_property': 'some_value',
                    'switch-power': True
                }
            }
        }

        updated_switch = await self.wall_switch_service.update(self.test_switch)
        self.assertTrue(updated_switch.switch_power)
        # Other properties should maintain their default values
        self.assertEqual(updated_switch.single_press_type, SinglePressType.CLASSIC)
        self.assertFalse(updated_switch.switch_iot)


if __name__ == '__main__':
    unittest.main() 