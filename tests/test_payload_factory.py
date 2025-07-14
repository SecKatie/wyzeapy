import unittest
from wyzeapy.payload_factory import (
    ford_create_payload,
    olive_create_get_payload,
    olive_create_post_payload,
    olive_create_hms_payload,
    olive_create_user_info_payload,
    olive_create_hms_get_payload,
    olive_create_hms_patch_payload,
    devicemgmt_create_capabilities_payload,
    devicemgmt_get_iot_props_list,
)
from wyzeapy.crypto import olive_create_signature
from unittest.mock import patch


class TestPayloadFactory(unittest.TestCase):
    @patch("wyzeapy.payload_factory.ford_create_signature")
    @patch("time.time", return_value=1234567890.123)
    def test_ford_create_payload(self, mock_time, mock_create_signature):
        mock_create_signature.return_value = "mock_signature"
        access_token = "test_access_token"
        payload = {"param1": "value1"}
        url_path = "/test/path"
        request_method = "POST"

        result = ford_create_payload(access_token, payload, url_path, request_method)

        self.assertEqual(result["access_token"], access_token)
        self.assertEqual(
            result["key"], "275965684684dbdaf29a0ed9"
        )  # FORD_APP_KEY from const.py
        self.assertEqual(result["timestamp"], "1234567890123")
        self.assertEqual(result["sign"], "mock_signature")
        mock_create_signature.assert_called_once_with(url_path, request_method, result)

    @patch("time.time", return_value=1234567890.123)
    def test_olive_create_get_payload(self, mock_time):
        device_mac = "test_mac"
        keys = "key1,key2"

        result = olive_create_get_payload(device_mac, keys)

        self.assertEqual(result["keys"], keys)
        self.assertEqual(result["did"], device_mac)
        self.assertEqual(result["nonce"], 1234567890123)

    @patch("time.time", return_value=1234567890.123)
    def test_olive_create_post_payload(self, mock_time):
        device_mac = "test_mac"
        device_model = "test_model"
        prop_key = "test_prop"
        value = "test_value"

        result = olive_create_post_payload(device_mac, device_model, prop_key, value)

        self.assertEqual(result["did"], device_mac)
        self.assertEqual(result["model"], device_model)
        self.assertEqual(result["props"], {prop_key: value})
        self.assertEqual(result["is_sub_device"], 0)
        self.assertEqual(result["nonce"], "1234567890123")

    @patch("time.time", return_value=1234567890.123)
    def test_olive_create_hms_payload(self, mock_time):
        result = olive_create_hms_payload()
        self.assertEqual(result["group_id"], "hms")
        self.assertEqual(result["nonce"], "1234567890123")

    @patch("time.time", return_value=1234567890.123)
    def test_olive_create_user_info_payload(self, mock_time):
        result = olive_create_user_info_payload()
        self.assertEqual(result["nonce"], "1234567890123")

    @patch("time.time", return_value=1234567890.123)
    def test_olive_create_hms_get_payload(self, mock_time):
        hms_id = "test_hms_id"
        result = olive_create_hms_get_payload(hms_id)
        self.assertEqual(result["hms_id"], hms_id)
        self.assertEqual(result["nonce"], "1234567890123")

    def test_olive_create_hms_patch_payload(self):
        hms_id = "test_hms_id"
        result = olive_create_hms_patch_payload(hms_id)
        self.assertEqual(result["hms_id"], hms_id)

    def test_devicemgmt_create_capabilities_payload_floodlight(self):
        result = devicemgmt_create_capabilities_payload("floodlight", "on")
        self.assertEqual(result["name"], "floodlight")
        self.assertEqual(result["properties"][0]["prop"], "on")

    def test_devicemgmt_create_capabilities_payload_spotlight(self):
        result = devicemgmt_create_capabilities_payload("spotlight", "on")
        self.assertEqual(result["name"], "spotlight")
        self.assertEqual(result["properties"][0]["prop"], "on")

    def test_devicemgmt_create_capabilities_payload_power(self):
        result = devicemgmt_create_capabilities_payload("power", "test_value")
        self.assertEqual(result["name"], "iot-device")
        self.assertEqual(result["functions"][0]["name"], "test_value")

    def test_devicemgmt_create_capabilities_payload_siren(self):
        result = devicemgmt_create_capabilities_payload("siren", "test_value")
        self.assertEqual(result["name"], "siren")
        self.assertEqual(result["functions"][0]["name"], "test_value")

    def test_devicemgmt_create_capabilities_payload_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            devicemgmt_create_capabilities_payload("unsupported_type", "value")

    def test_devicemgmt_get_iot_props_list_LD_CFP(self):
        result = devicemgmt_get_iot_props_list("LD_CFP")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["name"], "camera")

    def test_devicemgmt_get_iot_props_list_AN_RSCW(self):
        result = devicemgmt_get_iot_props_list("AN_RSCW")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["name"], "camera")

    def test_devicemgmt_get_iot_props_list_GW_GC1(self):
        result = devicemgmt_get_iot_props_list("GW_GC1")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["name"], "camera")

    def test_devicemgmt_get_iot_props_list_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            devicemgmt_get_iot_props_list("unsupported_model")

    def test_olive_create_signature_with_string_payload(self):
        payload = "test_string_payload"
        access_token = "test_access_token"
        signature = olive_create_signature(payload, access_token)
        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 32)  # MD5 hash is 32 hex characters
