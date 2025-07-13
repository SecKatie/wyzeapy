import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.thermostat_service import (
    ThermostatService, Thermostat, HVACMode, FanMode,
    TemperatureUnit, Preset, HVACState, ThermostatProps
)
from wyzeapy.types import DeviceTypes
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestThermostatService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.thermostat_service = ThermostatService(auth_lib=self.mock_auth_lib)
        self.thermostat_service._thermostat_get_iot_prop = AsyncMock()
        self.thermostat_service._thermostat_set_iot_prop = AsyncMock()
        self.thermostat_service.get_object_list = AsyncMock()

        # Create test thermostat
        self.test_thermostat = Thermostat({
            "device_type": DeviceTypes.THERMOSTAT.value,
            "product_model": "WLPTH1",
            "mac": "THERM123",
            "nickname": "Test Thermostat",
            "device_params": {"ip": "192.168.1.100"},
            "raw_dict": {}
        })

    async def test_update_thermostat(self):
        self.thermostat_service._thermostat_get_iot_prop.return_value = {
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

        updated_thermostat = await self.thermostat_service.update(self.test_thermostat)

        self.assertEqual(updated_thermostat.temp_unit, TemperatureUnit.FAHRENHEIT)
        self.assertEqual(updated_thermostat.cool_set_point, 74)
        self.assertEqual(updated_thermostat.heat_set_point, 64)
        self.assertEqual(updated_thermostat.fan_mode, FanMode.AUTO)
        self.assertEqual(updated_thermostat.hvac_mode, HVACMode.AUTO)
        self.assertEqual(updated_thermostat.preset, Preset.HOME)
        self.assertEqual(updated_thermostat.temperature, 71.5)
        self.assertTrue(updated_thermostat.available)
        self.assertEqual(updated_thermostat.humidity, 50)
        self.assertEqual(updated_thermostat.hvac_state, HVACState.IDLE)

    async def test_get_thermostats(self):
        mock_thermostat = MagicMock()
        mock_thermostat.type = DeviceTypes.THERMOSTAT
        mock_thermostat.raw_dict = {
            "device_type": DeviceTypes.THERMOSTAT.value,
            "product_model": "WLPTH1",
            "mac": "THERM123"
        }

        self.thermostat_service.get_object_list.return_value = [mock_thermostat]

        thermostats = await self.thermostat_service.get_thermostats()
        
        self.assertEqual(len(thermostats), 1)
        self.assertIsInstance(thermostats[0], Thermostat)
        self.thermostat_service.get_object_list.assert_awaited_once()

    async def test_set_cool_point(self):
        await self.thermostat_service.set_cool_point(self.test_thermostat, 75)
        self.thermostat_service._thermostat_set_iot_prop.assert_awaited_with(
            self.test_thermostat,
            ThermostatProps.COOL_SP,
            75
        )

    async def test_set_heat_point(self):
        await self.thermostat_service.set_heat_point(self.test_thermostat, 68)
        self.thermostat_service._thermostat_set_iot_prop.assert_awaited_with(
            self.test_thermostat,
            ThermostatProps.HEAT_SP,
            68
        )

    async def test_set_hvac_mode(self):
        await self.thermostat_service.set_hvac_mode(self.test_thermostat, HVACMode.COOL)
        self.thermostat_service._thermostat_set_iot_prop.assert_awaited_with(
            self.test_thermostat,
            ThermostatProps.MODE_SYS,
            HVACMode.COOL.value
        )

    async def test_set_fan_mode(self):
        await self.thermostat_service.set_fan_mode(self.test_thermostat, FanMode.ON)
        self.thermostat_service._thermostat_set_iot_prop.assert_awaited_with(
            self.test_thermostat,
            ThermostatProps.FAN_MODE,
            FanMode.ON.value
        )

    async def test_set_preset(self):
        await self.thermostat_service.set_preset(self.test_thermostat, Preset.AWAY)
        self.thermostat_service._thermostat_set_iot_prop.assert_awaited_with(
            self.test_thermostat,
            ThermostatProps.CURRENT_SCENARIO,
            Preset.AWAY.value
        )

    async def test_update_with_invalid_property(self):
        self.thermostat_service._thermostat_get_iot_prop.return_value = {
            'data': {
                'props': {
                    'invalid_property': 'some_value',
                    'temperature': '71.5'
                }
            }
        }

        updated_thermostat = await self.thermostat_service.update(self.test_thermostat)
        self.assertEqual(updated_thermostat.temperature, 71.5)
        # Other properties should maintain their default values
        self.assertEqual(updated_thermostat.temp_unit, TemperatureUnit.FAHRENHEIT)
        self.assertEqual(updated_thermostat.cool_set_point, 74)
        self.assertEqual(updated_thermostat.heat_set_point, 64)


if __name__ == '__main__':
    unittest.main() 