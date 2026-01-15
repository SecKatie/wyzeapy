"""Tests for device control methods using mocks."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from wyzeapy import (
    WyzeLight,
    WyzeLock,
    WyzePlug,
    ActionFailedError,
    ApiRequestError,
)
from wyzeapy.utils import is_set, get_or_default
from wyzeapy.wyze_api_client.types import UNSET, Unset
from wyzeapy.wyze_api_client.models import Device


class TestUnsetUtilities:
    """Tests for Unset utility functions."""

    def test_is_set_returns_false_for_unset(self):
        """is_set(UNSET) should return False."""
        assert is_set(UNSET) is False

    def test_is_set_returns_true_for_value(self):
        """is_set(some_value) should return True."""
        assert is_set("hello") is True
        assert is_set(123) is True
        assert is_set(None) is True  # None is still a value, not Unset
        assert is_set([]) is True
        assert is_set({}) is True

    def test_get_or_default_returns_value_when_set(self):
        """get_or_default should return the value when it's set."""
        assert get_or_default("hello", "default") == "hello"
        assert get_or_default(123, 0) == 123
        assert get_or_default(None, "default") is None  # None is a valid value

    def test_get_or_default_returns_default_when_unset(self):
        """get_or_default should return the default when value is Unset."""
        assert get_or_default(UNSET, "default") == "default"
        assert get_or_default(UNSET, 42) == 42
        assert get_or_default(UNSET, None) is None

    def test_get_or_default_returns_none_by_default(self):
        """get_or_default should return None if no default specified."""
        assert get_or_default(UNSET) is None


def create_mock_device(
    nickname: str = "Test Device",
    mac: str = "AABBCCDD",
    product_model: str = "WLPA19",
    product_type: str = "Light",
    switch_state: int = 0,
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
    params = MagicMock()
    params.additional_properties = {"switch_state": switch_state}
    device.device_params = params

    return device


def create_mock_context():
    """Create a mock WyzeApiContext for testing."""
    ctx = MagicMock()
    ctx.ensure_token_valid = AsyncMock()
    ctx.get_main_client.return_value = MagicMock()
    ctx.get_lock_client.return_value = MagicMock()
    ctx.build_common_params.return_value = {
        "phone_system_type": "1",
        "app_version": "1.0",
        "phone_id": "test-phone",
        "access_token": "test-token",
    }
    ctx.access_token = "test-token"
    ctx.phone_id = "test-phone"
    ctx.nonce.return_value = "123456789"
    ctx.ford_create_signature.return_value = "test-signature"
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
