import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from wyzeapy.exceptions import UnknownApiError
from wyzeapy.services.air_purifier_service import (
    AIR_QUALITY_UPDATE_INTERVAL,
    AirPurifier,
    AirPurifierFanMode,
    AirPurifierService,
)
from wyzeapy.types import AirPurifierProps, DeviceTypes, PropertyIDs
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestAirPurifierService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.air_purifier_service = AirPurifierService(auth_lib=self.mock_auth_lib)
        self.air_purifier_service._get_property_list = AsyncMock()
        self.air_purifier_service._set_property = AsyncMock()
        self.air_purifier_service._get_iot_prop = AsyncMock()
        self.air_purifier_service._set_iot_prop = AsyncMock()
        self.air_purifier_service._get_air_prop = AsyncMock()
        self.air_purifier_service._query_air_history = AsyncMock()
        self.air_purifier_service.get_object_list = AsyncMock()
        self.air_purifier_service._get_air_prop.return_value = {
            "data": {"settings": {}}
        }
        self.air_purifier_service._query_air_history.return_value = {"data": []}

        self.test_air_purifier = AirPurifier(
            {
                "product_type": DeviceTypes.COMMON.value,
                "product_model": "CO_AP1",
                "mac": "AIRPURIFIER123",
                "nickname": "Test Air Purifier",
                "device_params": {"ip": "192.168.1.100"},
                "raw_dict": {},
            }
        )

    async def test_update_air_purifier(self):
        self.air_purifier_service._get_property_list.return_value = [
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1"),
        ]
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {
                "props": {
                    "iot_state": "connected",
                    "fan_mode": "auto",
                    "app_version": "1.0.18.0",
                    "sn": "SN123456789",
                    "wifi_mac": "AA:BB:CC:DD:EE:FF",
                }
            }
        }

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertTrue(updated_air_purifier.on)
        self.assertTrue(updated_air_purifier.available)
        self.assertEqual(updated_air_purifier.fan_mode, "auto")
        self.assertEqual(updated_air_purifier.app_version, "1.0.18.0")
        self.assertEqual(updated_air_purifier.sn, "SN123456789")
        self.assertEqual(updated_air_purifier.wifi_mac, "AA:BB:CC:DD:EE:FF")
        self.air_purifier_service._get_air_prop.assert_awaited_once()
        self.air_purifier_service._query_air_history.assert_awaited_once()

    @patch("wyzeapy.services.air_purifier_service.time.time", return_value=3700)
    async def test_update_keeps_device_state_when_air_quality_fails(self, _mock_time):
        self.air_purifier_service._get_property_list.return_value = [
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1"),
        ]
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {"props": {"iot_state": "connected", "fan_mode": "auto"}}
        }
        self.air_purifier_service._get_air_prop.side_effect = UnknownApiError(
            {"code": 5030}
        )

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertTrue(updated_air_purifier.on)
        self.assertTrue(updated_air_purifier.available)
        self.assertEqual(updated_air_purifier.fan_mode, "auto")
        self.assertIsNone(updated_air_purifier.aqi)
        self.assertEqual(updated_air_purifier.air_quality_updated_at, 3700)
        self.air_purifier_service._get_air_prop.assert_awaited_once()
        self.air_purifier_service._query_air_history.assert_not_awaited()

    @patch("wyzeapy.services.air_purifier_service.time.time", return_value=3700)
    async def test_update_refreshes_air_quality_when_stale(self, _mock_time):
        self.air_purifier_service._get_property_list.return_value = []
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {"props": {"iot_state": "connected"}}
        }
        self.air_purifier_service._query_air_history.return_value = {
            "data": [{"avg": -1, "max_aqi": 5}]
        }
        self.air_purifier_service._get_air_prop.return_value = {
            "data": {"settings": {"aqi": "6"}}
        }

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertEqual(updated_air_purifier.aqi, 6)
        self.assertEqual(updated_air_purifier.max_hourly_aqi, 5)
        self.assertEqual(updated_air_purifier.air_quality_updated_at, 3700)
        self.air_purifier_service._get_air_prop.assert_awaited_once()
        self.air_purifier_service._query_air_history.assert_awaited_once()

    @patch("wyzeapy.services.air_purifier_service.time.time")
    async def test_update_uses_cached_air_quality_before_interval(self, mock_time):
        mock_time.return_value = AIR_QUALITY_UPDATE_INTERVAL
        self.air_purifier_service._get_property_list.return_value = []
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {"props": {"iot_state": "connected"}}
        }
        self.test_air_purifier.air_quality_updated_at = 1
        self.test_air_purifier.aqi = 6
        self.test_air_purifier.max_hourly_aqi = 5

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertEqual(updated_air_purifier.aqi, 6)
        self.assertEqual(updated_air_purifier.max_hourly_aqi, 5)
        self.air_purifier_service._get_air_prop.assert_not_awaited()
        self.air_purifier_service._query_air_history.assert_not_awaited()

    @patch("wyzeapy.services.air_purifier_service.time.time")
    async def test_update_refreshes_air_quality_after_interval(self, mock_time):
        mock_time.return_value = AIR_QUALITY_UPDATE_INTERVAL + 1
        self.air_purifier_service._get_property_list.return_value = []
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {"props": {"iot_state": "connected"}}
        }
        self.test_air_purifier.air_quality_updated_at = 1
        self.air_purifier_service._query_air_history.return_value = {
            "data": [{"avg": -1, "max_aqi": 5}]
        }
        self.air_purifier_service._get_air_prop.return_value = {
            "data": {"settings": {"aqi": "6"}}
        }

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertEqual(updated_air_purifier.aqi, 6)
        self.assertEqual(updated_air_purifier.max_hourly_aqi, 5)
        self.air_purifier_service._get_air_prop.assert_awaited_once()
        self.air_purifier_service._query_air_history.assert_awaited_once()

    async def test_update_air_purifier_disconnected(self):
        self.air_purifier_service._get_property_list.return_value = [
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1"),
        ]
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {"props": {"iot_state": "disconnected"}}
        }

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertTrue(updated_air_purifier.on)
        self.assertFalse(updated_air_purifier.available)
        self.air_purifier_service._get_air_prop.assert_not_awaited()
        self.air_purifier_service._query_air_history.assert_not_awaited()

    async def test_update_with_invalid_property(self):
        self.air_purifier_service._get_property_list.return_value = []
        self.air_purifier_service._get_iot_prop.return_value = {
            "data": {
                "props": {
                    "invalid_property": "some_value",
                    "fan_mode": "sleep",
                }
            }
        }

        updated_air_purifier = await self.air_purifier_service.update(
            self.test_air_purifier
        )

        self.assertEqual(updated_air_purifier.fan_mode, "sleep")
        self.assertFalse(updated_air_purifier.on)

    @patch("wyzeapy.services.air_purifier_service.time.time", return_value=3700)
    async def test_update_air_quality(self, _mock_time):
        self.air_purifier_service._query_air_history.return_value = {
            "data": [{"avg": -1, "max_aqi": 5}]
        }
        self.air_purifier_service._get_air_prop.return_value = {
            "data": {"settings": {"aqi": "6"}}
        }

        updated_air_purifier = await self.air_purifier_service.update_air_quality(
            self.test_air_purifier
        )

        self.assertEqual(updated_air_purifier.aqi, 6)
        self.assertEqual(updated_air_purifier.max_hourly_aqi, 5)
        self.assertEqual(updated_air_purifier.max_hourly_aqi_start_time, 3600)
        self.assertEqual(updated_air_purifier.max_hourly_aqi_end_time, 3700)
        self.assertEqual(updated_air_purifier.air_quality_updated_at, 3700)
        self.air_purifier_service._get_air_prop.assert_awaited_once()
        self.air_purifier_service._query_air_history.assert_awaited_once_with(
            "https://wyze-earth-service.wyzecam.com/plugin/earth/query_air_history",
            self.test_air_purifier,
            3600,
            3700,
        )

    async def test_update_air_quality_without_hourly_aqi(self):
        self.air_purifier_service._query_air_history.return_value = {"data": []}
        self.air_purifier_service._get_air_prop.return_value = {
            "data": {"settings": {"aqi": "6"}}
        }

        updated_air_purifier = await self.air_purifier_service.update_air_quality(
            self.test_air_purifier
        )

        self.assertEqual(updated_air_purifier.aqi, 6)
        self.assertIsNone(updated_air_purifier.max_hourly_aqi)

    async def test_update_air_quality_without_aqi(self):
        self.air_purifier_service._query_air_history.return_value = {"data": []}
        self.air_purifier_service._get_air_prop.return_value = {
            "data": {"settings": {}}
        }
        self.test_air_purifier.aqi = 6
        self.test_air_purifier.max_hourly_aqi = 5

        updated_air_purifier = await self.air_purifier_service.update_air_quality(
            self.test_air_purifier
        )

        self.assertIsNone(updated_air_purifier.aqi)
        self.assertIsNone(updated_air_purifier.max_hourly_aqi)

    def test_air_quality_hour(self):
        with patch(
            "wyzeapy.services.air_purifier_service.time.time", return_value=3700
        ):
            begin_time, last_time = self.air_purifier_service._air_quality_hour()

        self.assertEqual(begin_time, 3600)
        self.assertEqual(last_time, 3700)

    def test_get_max_hourly_aqi_uses_latest_max_aqi(self):
        aqi = self.air_purifier_service._get_max_hourly_aqi(
            [
                {"avg": 1, "max_aqi": 0},
                {"avg": -1, "max_aqi": 8},
            ]
        )

        self.assertEqual(aqi, 8)

    def test_get_max_hourly_aqi_returns_zero_when_sample_has_data(self):
        aqi = self.air_purifier_service._get_max_hourly_aqi([{"avg": 0, "max_aqi": 0}])

        self.assertEqual(aqi, 0)

    def test_get_max_hourly_aqi_ignores_empty_sample(self):
        aqi = self.air_purifier_service._get_max_hourly_aqi([{"avg": -1, "max_aqi": 0}])

        self.assertIsNone(aqi)

    def test_get_max_hourly_aqi_without_max_aqi(self):
        aqi = self.air_purifier_service._get_max_hourly_aqi([{"avg": 4}])

        self.assertIsNone(aqi)

    async def test_get_air_purifiers(self):
        mock_air_purifier = MagicMock()
        mock_air_purifier.type = DeviceTypes.COMMON
        mock_air_purifier.product_model = "CO_AP1"
        mock_air_purifier.raw_dict = {
            "product_type": DeviceTypes.COMMON.value,
            "product_model": "CO_AP1",
            "mac": "AIRPURIFIER123",
            "nickname": "Test Air Purifier",
            "device_params": {"ip": "192.168.1.100"},
        }

        mock_other_device = MagicMock()
        mock_other_device.type = DeviceTypes.COMMON
        mock_other_device.product_model = "OTHER_MODEL"

        self.air_purifier_service.get_object_list.return_value = [
            mock_air_purifier,
            mock_other_device,
        ]

        air_purifiers = await self.air_purifier_service.get_air_purifiers()

        self.assertEqual(len(air_purifiers), 1)
        self.assertIsInstance(air_purifiers[0], AirPurifier)
        self.assertEqual(air_purifiers[0].product_model, "CO_AP1")
        self.air_purifier_service.get_object_list.assert_awaited_once()

    async def test_turn_on(self):
        await self.air_purifier_service.turn_on(self.test_air_purifier)

        self.air_purifier_service._set_property.assert_awaited_once_with(
            self.test_air_purifier, PropertyIDs.ON.value, "1"
        )

    async def test_turn_off(self):
        await self.air_purifier_service.turn_off(self.test_air_purifier)

        self.air_purifier_service._set_property.assert_awaited_once_with(
            self.test_air_purifier, PropertyIDs.ON.value, "0"
        )

    async def test_set_fan_mode_with_enum(self):
        await self.air_purifier_service.set_fan_mode(
            self.test_air_purifier, AirPurifierFanMode.TURBO
        )

        self.air_purifier_service._set_iot_prop.assert_awaited_once_with(
            "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic",
            self.test_air_purifier,
            AirPurifierProps.FAN_MODE.value,
            AirPurifierFanMode.TURBO.value,
        )

    async def test_set_fan_mode_with_string(self):
        await self.air_purifier_service.set_fan_mode(self.test_air_purifier, "mid")

        self.air_purifier_service._set_iot_prop.assert_awaited_once_with(
            "https://wyze-earth-service.wyzecam.com/plugin/earth/set_iot_prop_by_topic",
            self.test_air_purifier,
            AirPurifierProps.FAN_MODE.value,
            "mid",
        )

    async def test_air_purifier_get_iot_prop(self):
        await self.air_purifier_service._air_purifier_get_iot_prop(
            self.test_air_purifier
        )

        self.air_purifier_service._get_iot_prop.assert_awaited_once_with(
            "https://wyze-earth-service.wyzecam.com/plugin/earth/get_iot_prop",
            self.test_air_purifier,
            "iot_state,fan_mode,app_version,sn,wifi_mac",
        )

    async def test_air_purifier_get_air_prop(self):
        await self.air_purifier_service._air_purifier_get_air_prop(
            self.test_air_purifier
        )

        self.air_purifier_service._get_air_prop.assert_awaited_once_with(
            "https://wyze-earth-service.wyzecam.com/plugin/earth/get_air_prop",
            self.test_air_purifier,
            AirPurifierProps.AQI.value,
        )

    async def test_air_purifier_query_air_history(self):
        await self.air_purifier_service._air_purifier_query_air_history(
            self.test_air_purifier, begin_time=1000, last_time=2000
        )

        self.air_purifier_service._query_air_history.assert_awaited_once_with(
            "https://wyze-earth-service.wyzecam.com/plugin/earth/query_air_history",
            self.test_air_purifier,
            1000,
            2000,
        )


if __name__ == "__main__":
    unittest.main()
