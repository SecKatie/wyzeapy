"""Tests for device control methods using mocks."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from wyzeapy import (
    WyzeCamera,
    WyzeContactSensor,
    WyzeGateway,
    WyzeIrrigation,
    WyzeLeakSensor,
    WyzeLight,
    WyzeLock,
    WyzeMotionSensor,
    WyzePlug,
    WyzeSensor,
    WyzeThermostat,
    WyzeWallSwitch,
    ActionFailedError,
    ApiRequestError,
)
from wyzeapy.const import DEVICEMGMT_API_MODELS
from wyzeapy.models import CameraEvent, IrrigationZone, ThermostatState
from wyzeapy.utils import or_none
from wyzeapy.wyze_api_client.types import UNSET
from wyzeapy.wyze_api_client.models import Device


class TestOrNone:
    """Tests for or_none utility function."""

    def test_or_none_returns_none_for_unset(self):
        """or_none(UNSET) should return None."""
        assert or_none(UNSET) is None

    def test_or_none_returns_value_for_set(self):
        """or_none(value) should return the value when it's set."""
        assert or_none("hello") == "hello"
        assert or_none(123) == 123
        assert or_none(None) is None  # None is a valid value, not Unset
        assert or_none([]) == []
        assert or_none({}) == {}


def create_mock_device(
    nickname: str = "Test Device",
    mac: str = "AABBCCDD",
    product_model: str = "WLPA19",
    product_type: str = "Light",
    switch_state: int = 0,
    device_params: dict[str, object] | None = None,
) -> Device:
    """Create a mock Device object for testing."""
    device = MagicMock(spec=Device)
    device.nickname = nickname
    device.mac = mac
    device.product_model = product_model
    device.product_type = product_type
    device.firmware_ver = "1.0.0"
    device.hardware_ver = "1.0"
    device.parent_device_mac = UNSET
    device.conn_state = 1
    device.push_switch = 1

    # Set up device_params
    device_params_data: dict[str, object] = {"switch_state": switch_state}
    if device_params:
        device_params_data.update(device_params)
    params = MagicMock()
    params.additional_properties = device_params_data
    device.device_params = params

    return device


def create_mock_context():
    """Create a mock WyzeApiContext for testing."""
    ctx = MagicMock()
    ctx.main_client = AsyncMock(return_value=MagicMock())
    ctx.lock_client = AsyncMock(return_value=MagicMock())
    ctx.platform_client = AsyncMock(return_value=MagicMock())
    ctx.app_client = AsyncMock(return_value=MagicMock())
    ctx.devicemgmt_client = AsyncMock(return_value=MagicMock())
    ctx.get_access_token = AsyncMock(return_value="test-token")
    ctx.build_common_params.return_value = {
        "phone_system_type": "1",
        "app_version": "1.0",
        "phone_id": "test-phone",
        "access_token": "test-token",
    }
    ctx.phone_id = "test-phone"
    ctx.nonce.return_value = "123456789"
    ctx.ford_create_signature.return_value = "test-signature"
    ctx.olive_create_signature.return_value = "test-signature"
    return ctx


class TestWyzeLightControl:
    """Tests for WyzeLight control methods."""

    @pytest.fixture
    def mock_light(self):
        """Create a WyzeLight with mocked context."""
        device = create_mock_device(
            nickname="Test Light",
            product_type="Light",
            switch_state=0,
        )
        light = WyzeLight(device, None)
        light._context = create_mock_context()
        return light

    @pytest.mark.asyncio
    async def test_turn_on_calls_run_action(self, mock_light):
        """turn_on() should call _run_action with POWER_ON."""
        with patch("wyzeapy.devices.base.run_action.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_run.return_value = mock_response

            await mock_light.turn_on()

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args.kwargs["body"].action_key.value == "power_on"

    @pytest.mark.asyncio
    async def test_turn_on_raises_on_null_response(self, mock_light):
        """turn_on() should raise ActionFailedError when response is None."""
        with patch("wyzeapy.devices.base.run_action.asyncio") as mock_run:
            mock_run.return_value = None

            with pytest.raises(ActionFailedError) as exc_info:
                await mock_light.turn_on()

            assert "power_on" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_turn_on_raises_on_error_code(self, mock_light):
        """turn_on() should raise ActionFailedError when code != '1'."""
        with patch("wyzeapy.devices.base.run_action.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "0"  # Error code
            mock_run.return_value = mock_response

            with pytest.raises(ActionFailedError):
                await mock_light.turn_on()

    @pytest.mark.asyncio
    async def test_turn_off_calls_run_action(self, mock_light):
        """turn_off() should call _run_action with POWER_OFF."""
        with patch("wyzeapy.devices.base.run_action.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_run.return_value = mock_response

            await mock_light.turn_off()

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args.kwargs["body"].action_key.value == "power_off"

    @pytest.mark.asyncio
    async def test_set_brightness_clamps_to_max(self, mock_light):
        """set_brightness() should clamp values above 100 to 100."""
        with patch("wyzeapy.devices.base.set_property.asyncio") as mock_set:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_set.return_value = mock_response

            await mock_light.set_brightness(150)

            mock_set.assert_called_once()
            call_args = mock_set.call_args
            assert call_args.kwargs["body"].pvalue == "100"

    @pytest.mark.asyncio
    async def test_set_brightness_clamps_to_min(self, mock_light):
        """set_brightness() should clamp values below 0 to 0."""
        with patch("wyzeapy.devices.base.set_property.asyncio") as mock_set:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_set.return_value = mock_response

            await mock_light.set_brightness(-50)

            mock_set.assert_called_once()
            call_args = mock_set.call_args
            assert call_args.kwargs["body"].pvalue == "0"

    @pytest.mark.asyncio
    async def test_set_brightness_raises_on_failure(self, mock_light):
        """set_brightness() should raise ActionFailedError on failure."""
        with patch("wyzeapy.devices.base.set_property.asyncio") as mock_set:
            mock_set.return_value = None

            with pytest.raises(ActionFailedError):
                await mock_light.set_brightness(50)


class TestWyzeLockControl:
    """Tests for WyzeLock control methods."""

    @pytest.fixture
    def mock_lock(self):
        """Create a WyzeLock with mocked context."""
        device = create_mock_device(
            nickname="Test Lock",
            product_type="Lock",
            product_model="WLCK1",
            switch_state=0,  # 0 = locked
        )
        lock = WyzeLock(device, None)
        lock._context = create_mock_context()
        return lock

    @pytest.mark.asyncio
    async def test_lock_calls_lock_control(self, mock_lock):
        """lock() should call lock_control API with REMOTELOCK action."""
        with patch("wyzeapy.devices.lock.lock_control.asyncio") as mock_ctrl:
            mock_response = MagicMock()
            mock_response.code = 0  # Lock API uses 0 for success
            mock_ctrl.return_value = mock_response

            await mock_lock.lock()

            mock_ctrl.assert_called_once()
            call_args = mock_ctrl.call_args
            assert call_args.kwargs["body"].action.value == "remoteLock"

    @pytest.mark.asyncio
    async def test_unlock_calls_lock_control(self, mock_lock):
        """unlock() should call lock_control API with REMOTEUNLOCK action."""
        with patch("wyzeapy.devices.lock.lock_control.asyncio") as mock_ctrl:
            mock_response = MagicMock()
            mock_response.code = 0
            mock_ctrl.return_value = mock_response

            await mock_lock.unlock()

            mock_ctrl.assert_called_once()
            call_args = mock_ctrl.call_args
            assert call_args.kwargs["body"].action.value == "remoteUnlock"

    @pytest.mark.asyncio
    async def test_lock_raises_on_null_response(self, mock_lock):
        """lock() should raise ActionFailedError when response is None."""
        with patch("wyzeapy.devices.lock.lock_control.asyncio") as mock_ctrl:
            mock_ctrl.return_value = None

            with pytest.raises(ActionFailedError) as exc_info:
                await mock_lock.lock()

            assert "remoteLock" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_lock_raises_on_error_code(self, mock_lock):
        """lock() should raise ActionFailedError when code != 0."""
        with patch("wyzeapy.devices.lock.lock_control.asyncio") as mock_ctrl:
            mock_response = MagicMock()
            mock_response.code = 1  # Error code (lock uses 0 for success)
            mock_ctrl.return_value = mock_response

            with pytest.raises(ActionFailedError):
                await mock_lock.lock()

    def test_is_locked_property(self, mock_lock):
        """is_locked should return True when switch_state is 0."""
        assert mock_lock.is_locked is True

    def test_is_locked_property_false(self, mock_lock):
        """is_locked should return False when switch_state is not 0."""
        mock_lock._device.device_params.additional_properties["switch_state"] = 1
        assert mock_lock.is_locked is False

    @pytest.mark.asyncio
    async def test_get_lock_info_raises_on_failure(self, mock_lock):
        """get_lock_info() should raise ApiRequestError when response is None."""
        with patch("wyzeapy.devices.lock.get_lock_info.asyncio") as mock_get:
            mock_get.return_value = None

            with pytest.raises(ApiRequestError) as exc_info:
                await mock_lock.get_lock_info()

            assert "get_lock_info" in str(exc_info.value)


class TestWyzePlugControl:
    """Tests for WyzePlug control methods."""

    @pytest.fixture
    def mock_plug(self):
        """Create a WyzePlug with mocked context."""
        device = create_mock_device(
            nickname="Test Plug",
            product_type="Plug",
            product_model="WLPP1",
            switch_state=1,
        )
        plug = WyzePlug(device, None)
        plug._context = create_mock_context()
        return plug

    @pytest.mark.asyncio
    async def test_turn_on_calls_run_action(self, mock_plug):
        """turn_on() should work for plugs (inherited from SwitchableDeviceMixin)."""
        with patch("wyzeapy.devices.base.run_action.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_run.return_value = mock_response

            await mock_plug.turn_on()

            mock_run.assert_called_once()

    def test_is_on_property(self, mock_plug):
        """is_on should return True when switch_state is 1."""
        assert mock_plug.is_on is True

    def test_is_on_property_false(self, mock_plug):
        """is_on should return False when switch_state is 0."""
        mock_plug._device.device_params.additional_properties["switch_state"] = 0
        assert mock_plug.is_on is False

    @pytest.mark.asyncio
    async def test_get_usage_history_raises_on_failure(self, mock_plug):
        """get_usage_history() should raise ApiRequestError when response is None."""
        with patch("wyzeapy.devices.plug.get_plug_usage_history.asyncio") as mock_get:
            mock_get.return_value = None

            with pytest.raises(ApiRequestError) as exc_info:
                await mock_plug.get_usage_history(1000, 2000)

            assert "get_plug_usage_history" in str(exc_info.value)


class TestWyzeWallSwitchControl:
    """Tests for WyzeWallSwitch control methods."""

    @pytest.fixture
    def mock_switch(self):
        """Create a WyzeWallSwitch with mocked context."""
        device = create_mock_device(
            nickname="Test Wall Switch",
            product_type="WallSwitch",
            product_model="WSW1",
            device_params={"switch-power": "off"},
        )
        wall_switch = WyzeWallSwitch(device, None)
        wall_switch._context = create_mock_context()
        return wall_switch

    @pytest.mark.asyncio
    async def test_turn_on_calls_run_action(self, mock_switch):
        """turn_on() should call run_action with POWER_ON."""
        with patch("wyzeapy.devices.base.run_action.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_run.return_value = mock_response

            await mock_switch.turn_on()

            mock_run.assert_called_once()
            assert mock_run.call_args.kwargs["body"].action_key.value == "power_on"

    def test_is_on_property(self, mock_switch):
        """is_on should be False when switch-power is off."""
        assert mock_switch.is_on is False


class TestWyzeCameraControl:
    """Tests for WyzeCamera control methods."""

    @pytest.fixture
    def mock_camera(self):
        """Create a WyzeCamera with mocked context."""
        if not DEVICEMGMT_API_MODELS:
            pytest.skip("No device management camera models configured")
        model = next(iter(DEVICEMGMT_API_MODELS))
        device = create_mock_device(
            nickname="Test Camera",
            product_type="Camera",
            product_model=model,
        )
        camera = WyzeCamera(device, None)
        camera._context = create_mock_context()
        return camera

    @pytest.mark.asyncio
    async def test_get_events_returns_events(self, mock_camera):
        """get_events() should return parsed CameraEvent list."""
        with patch("wyzeapy.devices.camera.get_event_list.asyncio") as mock_get:
            event = MagicMock()
            event.to_dict.return_value = {"event_id": "1"}
            response = MagicMock()
            response.data = MagicMock()
            response.data.event_list = [event]
            mock_get.return_value = response

            events = await mock_camera.get_events()

            assert len(events) == 1
            assert isinstance(events[0], CameraEvent)

    @pytest.mark.asyncio
    async def test_get_events_raises_on_failure(self, mock_camera):
        """get_events() should raise ApiRequestError when response is None."""
        with patch("wyzeapy.devices.camera.get_event_list.asyncio") as mock_get:
            mock_get.return_value = None

            with pytest.raises(ApiRequestError):
                await mock_camera.get_events()

    @pytest.mark.asyncio
    async def test_floodlight_on_calls_devicemgmt(self, mock_camera):
        """floodlight_on() should call device management API."""
        with patch("wyzeapy.devices.camera.device_mgmt_run_action.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_run.return_value = mock_response

            await mock_camera.floodlight_on()

            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_floodlight_on_raises_on_failure(self, mock_camera):
        """floodlight_on() should raise ActionFailedError on failure."""
        with patch("wyzeapy.devices.camera.device_mgmt_run_action.asyncio") as mock_run:
            mock_run.return_value = None

            with pytest.raises(ActionFailedError):
                await mock_camera.floodlight_on()


class TestWyzeThermostatControl:
    """Tests for WyzeThermostat control methods."""

    @pytest.fixture
    def mock_thermostat(self):
        """Create a WyzeThermostat with mocked context."""
        device = create_mock_device(
            nickname="Test Thermostat",
            product_type="Thermostat",
            product_model="WV1",
        )
        thermostat = WyzeThermostat(device, None)
        thermostat._context = create_mock_context()
        return thermostat

    @pytest.mark.asyncio
    async def test_get_state_returns_state(self, mock_thermostat):
        """get_state() should return a ThermostatState."""
        with patch("wyzeapy.devices.thermostat.get_thermostat_iot_prop.asyncio") as mock_get:
            response = MagicMock()
            response.to_dict.return_value = {"temp_unit": "F"}
            mock_get.return_value = response

            state = await mock_thermostat.get_state()

            assert isinstance(state, ThermostatState)

    @pytest.mark.asyncio
    async def test_get_state_raises_on_failure(self, mock_thermostat):
        """get_state() should raise ApiRequestError when response is None."""
        with patch("wyzeapy.devices.thermostat.get_thermostat_iot_prop.asyncio") as mock_get:
            mock_get.return_value = None

            with pytest.raises(ApiRequestError):
                await mock_thermostat.get_state()

    @pytest.mark.asyncio
    async def test_set_heat_setpoint_calls_api(self, mock_thermostat):
        """set_heat_setpoint() should call thermostat API."""
        with patch("wyzeapy.devices.thermostat.set_thermostat_iot_prop.asyncio") as mock_set:
            mock_response = MagicMock()
            mock_response.code = "1"
            mock_set.return_value = mock_response

            await mock_thermostat.set_heat_setpoint(70)

            mock_set.assert_called_once()
            assert mock_set.call_args.kwargs["body"].props["heat_sp"] == 70

    @pytest.mark.asyncio
    async def test_set_heat_setpoint_raises_on_failure(self, mock_thermostat):
        """set_heat_setpoint() should raise ActionFailedError on failure."""
        with patch("wyzeapy.devices.thermostat.set_thermostat_iot_prop.asyncio") as mock_set:
            mock_response = MagicMock()
            mock_response.code = "0"
            mock_set.return_value = mock_response

            with pytest.raises(ActionFailedError):
                await mock_thermostat.set_heat_setpoint(70)


class TestWyzeIrrigationControl:
    """Tests for WyzeIrrigation control methods."""

    @pytest.fixture
    def mock_irrigation(self):
        """Create a WyzeIrrigation with mocked context."""
        device = create_mock_device(
            nickname="Test Irrigation",
            product_type="Common",
            product_model="WIRR1",
        )
        irrigation = WyzeIrrigation(device, None)
        irrigation._context = create_mock_context()
        return irrigation

    @pytest.mark.asyncio
    async def test_get_zones_returns_zones(self, mock_irrigation):
        """get_zones() should return parsed IrrigationZone list."""
        with patch("wyzeapy.devices.irrigation.get_irrigation_zones.asyncio") as mock_get:
            zone = MagicMock()
            zone.to_dict.return_value = {"zone_id": "1"}
            response = MagicMock()
            response.data = MagicMock()
            response.data.zones = [zone]
            mock_get.return_value = response

            zones = await mock_irrigation.get_zones()

            assert len(zones) == 1
            assert isinstance(zones[0], IrrigationZone)

    @pytest.mark.asyncio
    async def test_get_zones_raises_on_failure(self, mock_irrigation):
        """get_zones() should raise ApiRequestError when response is None."""
        with patch("wyzeapy.devices.irrigation.get_irrigation_zones.asyncio") as mock_get:
            mock_get.return_value = None

            with pytest.raises(ApiRequestError):
                await mock_irrigation.get_zones()

    @pytest.mark.asyncio
    async def test_run_raises_on_failure(self, mock_irrigation):
        """run() should raise ActionFailedError when API fails."""
        with patch("wyzeapy.devices.irrigation.irrigation_quick_run.asyncio") as mock_run:
            mock_response = MagicMock()
            mock_response.code = "0"
            mock_run.return_value = mock_response

            with pytest.raises(ActionFailedError):
                await mock_irrigation.run([(1, 60)])


class TestWyzeSensorProperties:
    """Tests for WyzeSensor properties."""

    def test_battery_properties(self):
        """Battery mixin should return expected values."""
        device = create_mock_device(
            nickname="Test Sensor",
            product_type="ContactSensor",
            device_params={"is_low_battery": 1, "battery": 55},
        )
        sensor = WyzeSensor(device, None)
        assert sensor.is_low_battery is True
        assert sensor.battery_level == 55

    def test_contact_sensor_properties(self):
        """Contact sensor should report open state."""
        device = create_mock_device(
            nickname="Test Contact",
            product_type="ContactSensor",
            device_params={"open_close_state": 1},
        )
        sensor = WyzeContactSensor(device, None)
        assert sensor.is_open is True

    def test_motion_sensor_properties(self):
        """Motion sensor should report motion state."""
        device = create_mock_device(
            nickname="Test Motion",
            product_type="MotionSensor",
            device_params={"motion_state": 1},
        )
        sensor = WyzeMotionSensor(device, None)
        assert sensor.motion_detected is True

    def test_leak_sensor_properties(self):
        """Leak sensor should report leak state."""
        device = create_mock_device(
            nickname="Test Leak",
            product_type="LeakSensor",
            device_params={"leak_state": 1},
        )
        sensor = WyzeLeakSensor(device, None)
        assert sensor.leak_detected is True


class TestWyzeGateway:
    """Tests for WyzeGateway device."""

    def test_gateway_instantiation(self):
        """Gateway should initialize from device data."""
        device = create_mock_device(
            nickname="Test Gateway",
            product_type="gateway",
            product_model="GW1",
        )
        gateway = WyzeGateway(device, None)
        assert gateway.nickname == "Test Gateway"
        assert gateway.mac == "AABBCCDD"
