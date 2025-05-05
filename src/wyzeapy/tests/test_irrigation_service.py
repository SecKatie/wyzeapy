import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.irrigation_service import (
    IrrigationService, Irrigation, HVACMode, FanMode,
    TemperatureUnit, Preset, HVACState, IrrigationProps
)
from wyzeapy.types import DeviceTypes
from wyzeapy.wyze_auth_lib import WyzeAuthLib

# todo: add tests for irrigation service

class TestIrrigationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.irrigation_service = IrrigationService(auth_lib=self.mock_auth_lib)
        self.irrigation_service._irrigation_get_iot_prop = AsyncMock()
        self.irrigation_service._irrigation_set_iot_prop = AsyncMock()
        self.irrigation_service.get_object_list = AsyncMock()

        # Create test irrigation
        self.test_irrigation = Irrigation({
            "device_type": DeviceTypes.THERMOSTAT.value,
            "product_model": "WLPTH1",
            "mac": "IRRIG123",
            "nickname": "Test Irrigation",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_irrigation(self):
        self.irrigation_service._irrigation_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'temp_unit': 'F',
                    'cool_sp': '74',
                    'heat_sp': '64',
                    'fan_mode': 'auto',
                    'mode_sys': 'auto',
                    'current_scenario': 'home',
                    'temperature': '71.5',
                    'iot_state': 'connected',
                    'humidity': '50',
                    'working_state': 'idle'
                }
            }
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)

        self.assertEqual(updated_irrigation.temp_unit, TemperatureUnit.FAHRENHEIT)
        self.assertEqual(updated_irrigation.cool_set_point, 74)
        self.assertEqual(updated_irrigation.heat_set_point, 64)
        self.assertEqual(updated_irrigation.fan_mode, FanMode.AUTO)
        self.assertEqual(updated_irrigation.hvac_mode, HVACMode.AUTO)
        self.assertEqual(updated_irrigation.preset, Preset.HOME)
        self.assertEqual(updated_irrigation.temperature, 71.5)
        self.assertTrue(updated_irrigation.available)
        self.assertEqual(updated_irrigation.humidity, 50)
        self.assertEqual(updated_irrigation.hvac_state, HVACState.IDLE)

    async def test_get_irrigations(self):
        mock_irrigation = MagicMock()
        mock_irrigation.type = DeviceTypes.THERMOSTAT
        mock_irrigation.raw_dict = {
            "device_type": DeviceTypes.THERMOSTAT.value,
            "product_model": "WLPTH1",
            "mac": "IRRIG123"
        }

        self.irrigation_service.get_object_list.return_value = [mock_irrigation]

        irrigations = await self.irrigation_service.get_irrigations()
        
        self.assertEqual(len(irrigations), 1)
        self.assertIsInstance(irrigations[0], Irrigation)
        self.irrigation_service.get_object_list.assert_awaited_once()

    async def test_set_cool_point(self):
        await self.irrigation_service.set_cool_point(self.test_irrigation, 75)
        self.irrigation_service._irrigation_set_iot_prop.assert_awaited_with(
            self.test_irrigation,
            IrrigationProps.COOL_SP,
            75
        )

    async def test_set_heat_point(self):
        await self.irrigation_service.set_heat_point(self.test_irrigation, 68)
        self.irrigation_service._irrigation_set_iot_prop.assert_awaited_with(
            self.test_irrigation,
            IrrigationProps.HEAT_SP,
            68
        )

    async def test_set_hvac_mode(self):
        await self.irrigation_service.set_hvac_mode(self.test_irrigation, HVACMode.COOL)
        self.irrigation_service._irrigation_set_iot_prop.assert_awaited_with(
            self.test_irrigation,
            IrrigationProps.MODE_SYS,
            HVACMode.COOL.value
        )

    async def test_set_fan_mode(self):
        await self.irrigation_service.set_fan_mode(self.test_irrigation, FanMode.ON)
        self.irrigation_service._irrigation_set_iot_prop.assert_awaited_with(
            self.test_irrigation,
            IrrigationProps.FAN_MODE,
            FanMode.ON.value
        )

    async def test_set_preset(self):
        await self.irrigation_service.set_preset(self.test_irrigation, Preset.AWAY)
        self.irrigation_service._irrigation_set_iot_prop.assert_awaited_with(
            self.test_irrigation,
            IrrigationProps.CURRENT_SCENARIO,
            Preset.AWAY.value
        )

    async def test_update_with_invalid_property(self):
        self.irrigation_service._irrigation_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'invalid_property': 'some_value',
                    'temperature': '71.5'
                }
            }
        }

        updated_irrigation = await self.irrigation_service.update(self.test_irrigation)
        self.assertEqual(updated_irrigation.temperature, 71.5)
        # Other properties should maintain their default values
        self.assertEqual(updated_irrigation.temp_unit, TemperatureUnit.FAHRENHEIT)
        self.assertEqual(updated_irrigation.cool_set_point, 74)
        self.assertEqual(updated_irrigation.heat_set_point, 64)


if __name__ == '__main__':
    unittest.main() 