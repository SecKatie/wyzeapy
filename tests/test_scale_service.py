import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.scale_service import ScaleService, Scale, ScaleRecord
from wyzeapy.wyze_auth_lib import WyzeAuthLib


class TestScaleService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_auth_lib = MagicMock(spec=WyzeAuthLib)
        self.scale_service = ScaleService(auth_lib=self.mock_auth_lib)
        self.scale_service._scale_get = AsyncMock()
        self.scale_service.get_object_list = AsyncMock()

        self.test_scale = Scale(
            {
                "product_type": "Common",
                "product_model": "WL_SCU",
                "mac": "WL_SCU_000000000000",
                "nickname": "Bedroom Scale",
                "device_params": {},
                "raw_dict": {},
            }
        )

    async def test_get_scales(self):
        mock_device = MagicMock()
        mock_device.product_model = "WL_SCU"
        mock_device.raw_dict = {
            "product_type": "Common",
            "product_model": "WL_SCU",
            "mac": "WL_SCU_000000000000",
            "nickname": "Bedroom Scale",
            "device_params": {},
            "raw_dict": {},
        }
        self.scale_service.get_object_list.return_value = [mock_device]

        scales = await self.scale_service.get_scales()

        self.assertEqual(len(scales), 1)
        self.assertIsInstance(scales[0], Scale)
        self.scale_service.get_object_list.assert_awaited_once()

    async def test_get_scales_filters_non_scale_devices(self):
        mock_device = MagicMock()
        mock_device.product_model = "WLPP1"
        self.scale_service.get_object_list.return_value = [mock_device]

        scales = await self.scale_service.get_scales()

        self.assertEqual(len(scales), 0)

    async def test_update_with_list_response(self):
        self.scale_service._scale_get.return_value = {
            "code": 1,
            "data": [
                {
                    "weight": "90.7",
                    "bmi": "29.9",
                    "bmr": "1850.0",
                    "body_fat": "28.0",
                    "body_water": "55.0",
                    "bone_mineral": "3.8",
                    "muscle": "61.0",
                    "protein": "15.0",
                    "body_vfr": "10",
                    "metabolic_age": "45",
                    "heart_rate": None,
                    "user_id": "testuser123",
                    "family_member_id": None,
                }
            ],
        }

        updated = await self.scale_service.update(self.test_scale)

        self.assertIn("testuser123", updated.latest_by_member)
        record = updated.latest_by_member["testuser123"]
        self.assertAlmostEqual(record.weight, 90.7)
        self.assertAlmostEqual(record.bmi, 29.9)
        self.assertAlmostEqual(record.body_fat, 28.0)
        self.assertAlmostEqual(record.muscle, 61.0)
        self.assertAlmostEqual(record.body_water, 55.0)
        self.assertAlmostEqual(record.bone_mineral, 3.8)
        self.assertAlmostEqual(record.metabolic_age, 45.0)

    async def test_update_with_empty_response(self):
        self.scale_service._scale_get.return_value = {"code": 1, "data": []}

        updated = await self.scale_service.update(self.test_scale)

        self.assertEqual(len(updated.latest_by_member), 0)

    async def test_update_with_no_data(self):
        self.scale_service._scale_get.return_value = {"code": 1, "data": None}

        updated = await self.scale_service.update(self.test_scale)

        self.assertEqual(len(updated.latest_by_member), 0)

    async def test_scale_record_parsing(self):
        raw = {
            "weight": "90.7",
            "bmi": "29.9",
            "bmr": "1850.0",
            "body_fat": "28.0",
            "body_water": "55.0",
            "bone_mineral": "3.8",
            "muscle": "61.0",
            "protein": "15.0",
            "body_vfr": "10",
            "metabolic_age": "45",
            "heart_rate": "68",
            "user_id": "testuser123",
            "family_member_id": None,
        }
        record = ScaleRecord(raw)

        self.assertAlmostEqual(record.weight, 90.7)
        self.assertAlmostEqual(record.bmi, 29.9)
        self.assertAlmostEqual(record.heart_rate, 68.0)
        self.assertEqual(record.user_id, "testuser123")

    async def test_scale_record_handles_none_values(self):
        raw = {
            "weight": None,
            "bmi": "",
            "heart_rate": None,
            "user_id": "testuser123",
        }
        record = ScaleRecord(raw)

        self.assertIsNone(record.weight)
        self.assertIsNone(record.bmi)
        self.assertIsNone(record.heart_rate)


if __name__ == "__main__":
    unittest.main()
