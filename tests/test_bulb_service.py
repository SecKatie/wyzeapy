import unittest
from unittest.mock import AsyncMock, MagicMock
from wyzeapy.services.bulb_service import BulbService, Bulb
from wyzeapy.types import DeviceTypes, PropertyIDs


class TestBulbService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        mock_auth_lib = MagicMock()
        self.bulb_service = BulbService(auth_lib=mock_auth_lib)
        self.bulb_service._get_property_list = AsyncMock()
        self.bulb_service.get_updated_params = AsyncMock()

    async def test_update_bulb_basic_properties(self):
        mock_bulb = Bulb({
            "device_type": "Light",
            "product_model": "WLPA19",
            "mac": "TEST123",
            "raw_dict": {},
            "device_params": {"ip": "192.168.1.100"},
            "prop_map": {},
            'product_type': DeviceTypes.MESH_LIGHT.value
        })

        # Mock the property list response
        self.bulb_service._get_property_list.return_value = [
            (PropertyIDs.BRIGHTNESS, "75"),
            (PropertyIDs.COLOR_TEMP, "4000"),
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1")
        ]

        updated_bulb = await self.bulb_service.update(mock_bulb)

        self.assertEqual(updated_bulb.brightness, 75)
        self.assertEqual(updated_bulb.color_temp, 4000)
        self.assertTrue(updated_bulb.on)
        self.assertTrue(updated_bulb.available)

    async def test_update_bulb_lightstrip_properties(self):
        mock_bulb = Bulb({
            "device_type": "Light",
            "product_model": "WLST19",
            "mac": "TEST456",
            "raw_dict": {},
            "device_params": {"ip": "192.168.1.101"},
            "prop_map": {},
            'product_type': DeviceTypes.LIGHTSTRIP.value
        })
        mock_bulb.product_type = DeviceTypes.LIGHTSTRIP

        # Mock the property list response with the corrected color format (no # symbol)
        self.bulb_service._get_property_list.return_value = [
            (PropertyIDs.COLOR, "FF0000"),  # Removed the # symbol
            (PropertyIDs.COLOR_MODE, "1"),
            (PropertyIDs.LIGHTSTRIP_EFFECTS, "rainbow"),
            (PropertyIDs.LIGHTSTRIP_MUSIC_MODE, "1"),
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1")
        ]

        updated_bulb = await self.bulb_service.update(mock_bulb)

        self.assertEqual(updated_bulb.color, "FF0000")
        self.assertEqual(updated_bulb.color_mode, "1")
        self.assertEqual(updated_bulb.effects, "rainbow")
        self.assertTrue(updated_bulb.music_mode)
        self.assertTrue(updated_bulb.on)
        self.assertTrue(updated_bulb.available)

    async def test_update_bulb_sun_match(self):
        mock_bulb = Bulb({
            "device_type": "Light",
            "product_model": "WLPA19",
            "mac": "TEST789",
            "raw_dict": {},
            "device_params": {"ip": "192.168.1.102"},
            "prop_map": {},
            'product_type': DeviceTypes.MESH_LIGHT.value
        })

        # Mock the property list response
        self.bulb_service._get_property_list.return_value = [
            (PropertyIDs.SUN_MATCH, "1"),
            (PropertyIDs.ON, "1"),
            (PropertyIDs.AVAILABLE, "1")
        ]

        updated_bulb = await self.bulb_service.update(mock_bulb)

        self.assertTrue(updated_bulb.sun_match)
        self.assertTrue(updated_bulb.on)
        self.assertTrue(updated_bulb.available)

    async def test_update_bulb_invalid_color_temp(self):
        mock_bulb = Bulb({
            "device_type": "Light",
            "product_model": "WLPA19",
            "mac": "TEST101",
            "raw_dict": {},
            "device_params": {"ip": "192.168.1.103"},
            "prop_map": {},
            'product_type': DeviceTypes.MESH_LIGHT.value
        })

        # Mock the property list response with invalid color temp
        self.bulb_service._get_property_list.return_value = [
            (PropertyIDs.COLOR_TEMP, "invalid"),
            (PropertyIDs.ON, "1")
        ]

        updated_bulb = await self.bulb_service.update(mock_bulb)

        # Should default to 2700K when invalid
        self.assertEqual(updated_bulb.color_temp, 2700)
        self.assertTrue(updated_bulb.on)

    async def test_get_bulbs(self):
        mock_device = MagicMock()
        mock_device.type = DeviceTypes.LIGHT
        mock_device.raw_dict = {
            "device_type": "Light",
            "product_model": "WLPA19",
            "device_params": {"ip": "192.168.1.104"},
            "prop_map": {},
            'product_type': DeviceTypes.MESH_LIGHT.value
        }

        self.bulb_service.get_object_list = AsyncMock(return_value=[mock_device])

        bulbs = await self.bulb_service.get_bulbs()

        self.assertEqual(len(bulbs), 1)
        self.assertIsInstance(bulbs[0], Bulb)
        self.bulb_service.get_object_list.assert_awaited_once()