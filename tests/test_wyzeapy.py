import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from wyzeapy import Wyzeapy, TwoFactorAuthenticationEnabled
from wyzeapy.services.base_service import BaseService
from wyzeapy.wyze_auth_lib import WyzeAuthLib, Token


@pytest.fixture
def mock_auth_lib():
    with patch('wyzeapy.wyze_auth_lib.WyzeAuthLib.create', new_callable=AsyncMock) as mock_create:
        mock_auth_lib_instance = MagicMock(spec=WyzeAuthLib)
        mock_auth_lib_instance.token = Token("access", "refresh", 123)
        mock_auth_lib_instance.should_refresh = False
        mock_create.return_value = mock_auth_lib_instance
        yield mock_auth_lib_instance

@pytest.fixture
def mock_base_service():
    with patch('wyzeapy.services.base_service.BaseService', new_callable=MagicMock) as mock_service:
        yield mock_service

@pytest.mark.asyncio
async def test_create():
    wyze = await Wyzeapy.create()
    assert isinstance(wyze, Wyzeapy)

@pytest.mark.asyncio
async def test_login_success():
    with patch('wyzeapy.wyze_auth_lib.WyzeAuthLib.create', new_callable=AsyncMock) as mock_create:
        mock_auth_lib_instance = MagicMock(spec=WyzeAuthLib)
        mock_auth_lib_instance.token = Token("access", "refresh", 123)
        mock_auth_lib_instance.should_refresh = False
        mock_create.return_value = mock_auth_lib_instance

        wyze = await Wyzeapy.create()
        await wyze.login("test@example.com", "password", "key_id", "api_key")
        mock_create.assert_called_once()
        mock_auth_lib_instance.get_token_with_username_password.assert_called_once()
        assert isinstance(wyze._service, BaseService)

@pytest.mark.asyncio
async def test_login_with_token_success():
    with patch('wyzeapy.wyze_auth_lib.WyzeAuthLib.create', new_callable=AsyncMock) as mock_create:
        mock_auth_lib_instance = MagicMock(spec=WyzeAuthLib)
        mock_auth_lib_instance.token = Token("access", "refresh", 123)
        mock_auth_lib_instance.should_refresh = False
        mock_create.return_value = mock_auth_lib_instance

        wyze = await Wyzeapy.create()
        token = Token("access", "refresh", 123)
        await wyze.login("test@example.com", "password", "key_id", "api_key", token=token)
        mock_create.assert_called_once()
        mock_auth_lib_instance.refresh.assert_called_once()
        mock_auth_lib_instance.get_token_with_username_password.assert_not_called()
        assert isinstance(wyze._service, BaseService)

@pytest.mark.asyncio
async def test_login_2fa_enabled():
    with patch('wyzeapy.wyze_auth_lib.WyzeAuthLib.create', new_callable=AsyncMock) as mock_create:
        mock_auth_lib_instance = MagicMock(spec=WyzeAuthLib)
        mock_auth_lib_instance.token = Token("access", "refresh", 123)
        mock_auth_lib_instance.should_refresh = False
        mock_create.side_effect = TwoFactorAuthenticationEnabled("2FA required")

        wyze = await Wyzeapy.create()
        with pytest.raises(TwoFactorAuthenticationEnabled):
            await wyze.login("test@example.com", "password", "key_id", "api_key")

@pytest.mark.asyncio
async def test_login_with_2fa(mock_auth_lib):
    wyze = await Wyzeapy.create()
    wyze._auth_lib = mock_auth_lib # Manually set mock_auth_lib for this test
    mock_auth_lib.get_token_with_2fa = AsyncMock()
    token = await wyze.login_with_2fa("123456")
    mock_auth_lib.get_token_with_2fa.assert_called_once_with("123456")
    assert isinstance(wyze._service, BaseService)
    assert token == mock_auth_lib.token

@pytest.mark.asyncio
async def test_register_for_token_callback():
    wyze = await Wyzeapy.create()
    mock_callback = MagicMock()
    wyze.register_for_token_callback(mock_callback)
    assert mock_callback in wyze._token_callbacks

@pytest.mark.asyncio
async def test_unregister_for_token_callback():
    wyze = await Wyzeapy.create()
    mock_callback = MagicMock()
    wyze.register_for_token_callback(mock_callback)
    wyze.unregister_for_token_callback(mock_callback)
    assert mock_callback not in wyze._token_callbacks

@pytest.mark.asyncio
async def test_execute_token_callbacks_sync():
    wyze = await Wyzeapy.create()
    mock_callback = MagicMock()
    wyze.register_for_token_callback(mock_callback)
    token = Token("access", "refresh", 123)
    await wyze.execute_token_callbacks(token)
    mock_callback.assert_called_once_with(token)

@pytest.mark.asyncio
async def test_execute_token_callbacks_async():
    wyze = await Wyzeapy.create()
    mock_callback = AsyncMock()
    wyze.register_for_token_callback(mock_callback)
    token = Token("access", "refresh", 123)
    await wyze.execute_token_callbacks(token)
    mock_callback.assert_called_once_with(token)

@pytest.mark.asyncio
async def test_unique_device_ids(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    wyze._service.get_object_list = AsyncMock(return_value=[MagicMock(mac="mac1"), MagicMock(mac="mac2")])
    device_ids = await wyze.unique_device_ids
    assert device_ids == {"mac1", "mac2"}

@pytest.mark.asyncio
async def test_notifications_are_on(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    wyze._service.get_user_profile = AsyncMock(return_value={"data": {"notification": True}})
    assert await wyze.notifications_are_on is True

@pytest.mark.asyncio
async def test_enable_notifications(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    wyze._service.set_push_info = AsyncMock()
    await wyze.enable_notifications()
    wyze._service.set_push_info.assert_called_once_with(True)

@pytest.mark.asyncio
async def test_disable_notifications(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    wyze._service.set_push_info = AsyncMock()
    await wyze.disable_notifications()
    wyze._service.set_push_info.assert_called_once_with(False)

@pytest.mark.asyncio
async def test_valid_login_success(mock_auth_lib):
    mock_auth_lib.should_refresh = False
    is_valid = await Wyzeapy.valid_login("test@example.com", "password", "key_id", "api_key")
    assert is_valid is True

@pytest.mark.asyncio
async def test_valid_login_failure(mock_auth_lib):
    mock_auth_lib.should_refresh = True
    is_valid = await Wyzeapy.valid_login("test@example.com", "password", "key_id", "api_key")
    assert is_valid is False

@pytest.mark.asyncio
async def test_bulb_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.bulb_service
    assert service is not None
    assert wyze._bulb_service is service # Check lazy initialization

@pytest.mark.asyncio
async def test_switch_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.switch_service
    assert service is not None
    assert wyze._switch_service is service

@pytest.mark.asyncio
async def test_camera_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.camera_service
    assert service is not None
    assert wyze._camera_service is service

@pytest.mark.asyncio
async def test_thermostat_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.thermostat_service
    assert service is not None
    assert wyze._thermostat_service is service

@pytest.mark.asyncio
async def test_hms_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.hms_service
    assert service is not None
    assert wyze._hms_service is service

@pytest.mark.asyncio
async def test_lock_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.lock_service
    assert service is not None
    assert wyze._lock_service is service

@pytest.mark.asyncio
async def test_sensor_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.sensor_service
    assert service is not None
    assert wyze._sensor_service is service

@pytest.mark.asyncio
async def test_wall_switch_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.wall_switch_service
    assert service is not None
    assert wyze._wall_switch_service is service

@pytest.mark.asyncio
async def test_switch_usage_service(mock_auth_lib):
    wyze = await Wyzeapy.create()
    await wyze.login("test@example.com", "password", "key_id", "api_key")
    service = await wyze.switch_usage_service
    assert service is not None
    assert wyze._switch_usage_service is service
