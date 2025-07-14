import unittest
from wyzeapy.types import (
    Group,
    DeviceTypes,
    Device,
    Sensor,
    PropertyIDs,
    WallSwitchProps,
    ThermostatProps,
    ResponseCodes,
    ResponseCodesLock,
    File,
    Event,
    HMSStatus,
    DeviceMgmtToggleType,
    DeviceMgmtToggleProps,
)


class TestTypes(unittest.TestCase):
    def test_group_init_and_repr(self):
        data = {"group_id": "123", "group_name": "MyGroup"}
        group = Group(data)
        self.assertEqual(group.group_id, "123")
        self.assertEqual(group.group_name, "MyGroup")
        self.assertEqual(str(group), "<Group: 123, MyGroup>")

    def test_device_init_and_repr(self):
        data = {
            "product_type": "Light",
            "product_model": "WL1",
            "mac": "ABC",
            "nickname": "MyLight",
            "device_params": {},
        }
        device = Device(data)
        self.assertFalse(device.available)
        self.assertEqual(device.product_type, "Light")
        self.assertEqual(device.product_model, "WL1")
        self.assertEqual(device.mac, "ABC")
        self.assertEqual(device.nickname, "MyLight")
        self.assertEqual(device.type, DeviceTypes.LIGHT)
        self.assertEqual(str(device), "<Device: DeviceTypes.LIGHT, ABC>")

    def test_device_type_unknown(self):
        data = {
            "product_type": "UnknownType",
            "product_model": "UM1",
            "mac": "DEF",
            "nickname": "Unknown",
            "device_params": {},
        }
        device = Device(data)
        self.assertEqual(device.type, DeviceTypes.UNKNOWN)

    def test_sensor_init(self):
        data = {
            "product_type": "ContactSensor",
            "product_model": "CS1",
            "mac": "GHI",
            "nickname": "MySensor",
            "device_params": {"open_close_state": 0},
        }
        sensor = Sensor(data)
        self.assertEqual(sensor.type, DeviceTypes.CONTACT_SENSOR)

    def test_sensor_activity_detected_contact_sensor(self):
        data = {
            "product_type": "ContactSensor",
            "device_params": {"open_close_state": 1},
        }
        sensor = Sensor(data)
        self.assertEqual(sensor.activity_detected, 1)

    def test_sensor_activity_detected_motion_sensor(self):
        data = {"product_type": "MotionSensor", "device_params": {"motion_state": 1}}
        sensor = Sensor(data)
        self.assertEqual(sensor.activity_detected, 1)

    def test_sensor_activity_detected_assertion_error(self):
        data = {"product_type": "Light", "device_params": {}}
        sensor = Sensor(data)
        with self.assertRaises(AssertionError):
            sensor.activity_detected

    def test_sensor_is_low_battery(self):
        data = {"product_type": "ContactSensor", "device_params": {"is_low_battery": 1}}
        sensor = Sensor(data)
        self.assertEqual(sensor.is_low_battery, 1)

    def test_property_ids_enum(self):
        self.assertEqual(PropertyIDs.ON.value, "P3")
        self.assertEqual(PropertyIDs.BRIGHTNESS.value, "P1501")

    def test_wall_switch_props_enum(self):
        self.assertEqual(WallSwitchProps.IOT_STATE.value, "iot_state")

    def test_thermostat_props_enum(self):
        self.assertEqual(ThermostatProps.TEMPERATURE.value, "temperature")

    def test_response_codes_enum(self):
        self.assertEqual(ResponseCodes.SUCCESS.value, "1")

    def test_response_codes_lock_enum(self):
        self.assertEqual(ResponseCodesLock.SUCCESS.value, 0)

    def test_file_init(self):
        data = {
            "file_id": "f1",
            "type": 1,
            "url": "http://example.com/img.jpg",
            "status": 0,
            "en_algorithm": 0,
            "en_password": "",
            "is_ai": 0,
            "ai_tag_list": [],
            "ai_url": "",
            "file_params": {},
        }
        file_obj = File(data)
        self.assertEqual(file_obj.type, "Image")

        data["type"] = 2
        file_obj = File(data)
        self.assertEqual(file_obj.type, "Video")

    def test_event_init(self):
        data = {
            "event_id": "e1",
            "device_mac": "mac1",
            "device_model": "model1",
            "event_category": 1,
            "event_value": "val1",
            "event_ts": 123,
            "event_ack_result": 0,
            "is_feedback_correct": 0,
            "is_feedback_face": 0,
            "is_feedback_person": 0,
            "file_list": [],
            "event_params": {},
            "recognized_instance_list": [],
            "tag_list": [],
            "read_state": 0,
        }
        event = Event(data)
        self.assertEqual(event.event_id, "e1")
        self.assertEqual(event.device_mac, "mac1")

    def test_hms_status_enum(self):
        self.assertEqual(HMSStatus.HOME.value, "home")

    def test_device_mgmt_toggle_type_init(self):
        toggle_type = DeviceMgmtToggleType("page", "toggle")
        self.assertEqual(toggle_type.pageId, "page")
        self.assertEqual(toggle_type.toggleId, "toggle")

    def test_device_mgmt_toggle_props_enum(self):
        self.assertEqual(
            DeviceMgmtToggleProps.NOTIFICATION_TOGGLE.value.pageId, "cam_device_notify"
        )
