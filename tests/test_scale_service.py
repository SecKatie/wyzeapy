import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from wyzeapy.services.scale_service import (
    SCALE_MODELS,
    Scale,
    ScaleRecord,
    ScaleService,
)
from wyzeapy.types import DeviceTypes
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestScaleService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.scale_service = ScaleService(auth_lib=self.mock_auth_lib)
        self.scale_service.get_object_list = AsyncMock()
        self.scale_service._olive_get = AsyncMock()

        self.test_scale = Scale(
            {
                "product_type": DeviceTypes.SCALE.value,
                "product_model": "JA.SC",
                "mac": "JA.SC.ABCDEF123456",
                "nickname": "Test Scale",
                "device_params": {},
                "raw_dict": {},
            }
        )

    async def test_get_scales_filters_models(self):
        scale_device = Scale(
            {
                "product_type": DeviceTypes.SCALE.value,
                "product_model": "JA.SC",
                "mac": "JA.SC.111",
                "nickname": "Scale",
                "device_params": {},
            }
        )
        bulb = MagicMock()
        bulb.type = DeviceTypes.LIGHT
        bulb.product_model = "WLPA19"
        bulb.raw_dict = {
            "product_type": "Light",
            "product_model": "WLPA19",
            "mac": "BULB1",
            "nickname": "Bulb",
            "device_params": {},
        }
        pluto = Scale(
            {
                "product_type": "Common",
                "product_model": "WL_SC2",
                "mac": "WL_SC2.222",
                "nickname": "Scale S",
                "device_params": {},
            }
        )

        self.scale_service.get_object_list.return_value = [scale_device, bulb, pluto]

        scales = await self.scale_service.get_scales()

        self.assertEqual(len(scales), 2)
        self.assertEqual(scales[0].mac, "JA.SC.111")
        self.assertEqual(scales[1].mac, "WL_SC2.222")
        self.assertTrue(SCALE_MODELS.issuperset({"JA.SC", "WL_SC2"}))

    async def test_update_maps_latest_record(self):
        self.scale_service._olive_get.side_effect = [
            {
                "data": [
                    {
                        "id": "member1",
                        "nickname": "Chee",
                        "height": 175.0,
                        "goal_weight": 70.0,
                    }
                ]
            },
            {
                "data": [
                    {
                        "data_id": "rec1",
                        "measure_ts": 1700000000000,
                        "weight": 80.5,
                        "bmi": 24.1,
                        "body_fat": 18.5,
                        "muscle": 59.0,
                        "body_vfr": "10",
                        "body_water": -1,
                        "heart_rate": None,
                    }
                ]
            },
        ]

        updated = await self.scale_service.update(self.test_scale)

        self.assertTrue(updated.available)
        self.assertEqual(len(updated.family_members), 1)
        self.assertEqual(updated.family_members[0].nickname, "Chee")
        self.assertIsNotNone(updated.latest_record)
        assert updated.latest_record is not None
        self.assertEqual(updated.latest_record.weight_kg, 80.5)
        self.assertEqual(updated.latest_record.bmi, 24.1)
        self.assertEqual(updated.latest_record.body_fat, 18.5)
        self.assertEqual(updated.latest_record.muscle, 59.0)
        self.assertEqual(updated.latest_record.body_vfr, 10.0)
        self.assertIsNone(updated.latest_record.body_water)
        self.assertEqual(
            self.scale_service._olive_get.await_args_list[0].args[0],
            "https://wyze-scale-service.wyzecam.com/plugin/scale/get_family_member",
        )
        self.assertEqual(
            self.scale_service._olive_get.await_args_list[1].args[0],
            "https://wyze-scale-service.wyzecam.com/plugin/scale/get_latest_record",
        )
        self.assertEqual(
            self.scale_service._olive_get.await_args_list[1].kwargs["device_id"],
            "JA.SC.ABCDEF123456",
        )

    async def test_update_uses_pluto_urls(self):
        pluto_scale = Scale(
            {
                "product_type": DeviceTypes.SCALE.value,
                "product_model": "WL_SC2",
                "mac": "WL_SC2.ABCDEF",
                "nickname": "Scale S",
                "device_params": {},
            }
        )
        self.scale_service._olive_get.side_effect = [
            {"data": []},
            {"data": {"weight": 70.0, "bmi": 22.0, "measure_ts": 1}},
        ]

        await self.scale_service.update(pluto_scale)

        self.assertEqual(
            self.scale_service._olive_get.await_args_list[0].args[0],
            "https://wyze-pluto-service.wyzecam.com/plugin/pluto/get_family_member",
        )
        self.assertEqual(
            self.scale_service._olive_get.await_args_list[1].args[0],
            "https://wyze-pluto-service.wyzecam.com/plugin/pluto/get_latest_record",
        )

    async def test_update_empty_latest_record(self):
        self.scale_service._olive_get.return_value = {"data": []}

        updated = await self.scale_service.update(self.test_scale)

        self.assertTrue(updated.available)
        self.assertIsNone(updated.latest_record)

    async def test_get_records_range(self):
        self.scale_service._olive_get.return_value = {
            "data": [
                {"weight": 80.0, "bmi": 24.0, "measure_ts": 100},
                {"weight": 81.0, "bmi": 24.2, "measure_ts": 200},
            ]
        }

        records = await self.scale_service.get_records(
            self.test_scale,
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 31),
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].weight_kg, 80.0)
        call_kwargs = self.scale_service._olive_get.await_args.kwargs
        self.assertEqual(call_kwargs["device_id"], "JA.SC.ABCDEF123456")
        self.assertIn("start_time", call_kwargs)
        self.assertIn("end_time", call_kwargs)

    async def test_get_latest_record_ignores_other_scale_mac(self):
        self.scale_service._olive_get.side_effect = [
            {"data": [{"weight": 80.0, "measure_ts": 100, "mac": "WL_SCU.OTHER"}]},
            {
                "data": [
                    {"weight": 80.0, "measure_ts": 100, "mac": "WL_SCU.OTHER"},
                    {"weight": 70.0, "measure_ts": 90, "mac": "JA.SC.ABCDEF123456"},
                ]
            },
        ]

        record = await self.scale_service.get_latest_record(self.test_scale)

        self.assertIsNotNone(record)
        self.assertEqual(record.weight_kg, 70.0)
        self.assertEqual(self.scale_service._olive_get.await_count, 2)

    def test_record_prefers_device_id_for_matching(self):
        record = ScaleRecord(
            {
                "mac": "80:48:2c:95:5c:53",
                "device_id": "WL_SCU_80482C955C53",
                "weight": 77.9,
            }
        )
        scale = Scale(
            {
                "product_type": DeviceTypes.SCALE.value,
                "product_model": "JA.SC",
                "mac": "JA.SC.2CAA8E429AE3",
                "nickname": "Classic",
                "device_params": {},
            }
        )
        self.assertFalse(ScaleService._record_matches_scale(scale, record))
        self.assertTrue(
            ScaleService._mac_matches("JA.SC.ABCDEF123456", "ABCDEF123456")
        )
        self.assertTrue(
            ScaleService._mac_matches(
                "WL_SCU_80482C955C53", "WL_SCU.80482C955C53"
            )
        )
        self.assertFalse(
            ScaleService._mac_matches("JA.SC.ABCDEF123456", "OTHER123456")
        )

    async def test_get_latest_record_legacy_payload_without_mac(self):
        self.scale_service._olive_get.side_effect = [
            {"data": []},
            {"data": {"weight": 80.0, "measure_ts": 100}},
        ]

        record = await self.scale_service.get_latest_record(self.test_scale)

        self.assertIsNotNone(record)
        self.assertEqual(record.weight_kg, 80.0)

    async def test_get_latest_record_uses_record_range_when_mac_mismatch(self):
        self.scale_service._olive_get.side_effect = [
            {
                "data": [
                    {
                        "weight": 90.0,
                        "measure_ts": 200,
                        "mac": "80:48:2c:95:5c:53",
                        "device_id": "WL_SCU_80482C955C53",
                    }
                ]
            },
            {
                "data": [
                    {
                        "weight": 90.0,
                        "measure_ts": 200,
                        "mac": "80:48:2c:95:5c:53",
                        "device_id": "WL_SCU_80482C955C53",
                    }
                ]
            },
            {"data": []},
            {"data": []},
            {"data": []},
            {"data": []},
            {"data": []},
            {"data": []},
            {
                "data": [
                    {
                        "weight": 70.0,
                        "measure_ts": 1676942223004,
                        "mac": "ABCDEF123456",
                    }
                ]
            },
        ]

        record = await self.scale_service.get_latest_record(self.test_scale)

        self.assertIsNotNone(record)
        self.assertEqual(record.weight_kg, 70.0)
        self.assertEqual(self.scale_service._olive_get.await_count, 9)

    async def test_get_records_filters_other_scale_mac(self):
        self.scale_service._olive_get.return_value = {
            "data": [
                {"weight": 80.0, "measure_ts": 100, "mac": "JA.SC.ABCDEF123456"},
                {"weight": 90.0, "measure_ts": 200, "mac": "WL_SCU.OTHER_SCALE"},
            ]
        }

        records = await self.scale_service.get_records(
            self.test_scale,
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 31),
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].weight_kg, 80.0)

    def test_scale_record_sentinel_values(self):
        record = ScaleRecord(
            {
                "weight": 70.0,
                "body_fat": -1,
                "muscle": -1.0,
                "body_vfr": -1,
                "bmi": 22.5,
                "heart_rate": -1,
                "metabolic_age": -1,
            }
        )
        self.assertEqual(record.weight_kg, 70.0)
        self.assertEqual(record.bmi, 22.5)
        self.assertIsNone(record.body_fat)
        self.assertIsNone(record.muscle)
        self.assertIsNone(record.body_vfr)
        self.assertIsNone(record.heart_rate)
        self.assertIsNone(record.metabolic_age)


if __name__ == "__main__":
    unittest.main()
