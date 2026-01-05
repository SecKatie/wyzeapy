"""Tests for the Wyzeapy wrapper."""

import hashlib
import pytest

from wyzeapy import (
    Wyzeapy,
    Token,
    NotAuthenticatedError,
    WyzeDevice,
    WyzeCamera,
    WyzePlug,
    WyzeLock,
    WyzeLight,
    WyzeThermostat,
    WyzeSensor,
    WyzeUser,
    DeviceType,
)
from wyzeapy.utils import hash_password


class TestHashPassword:
    """Tests for password hashing."""

    def testhash_password_returns_md5(self):
        """Should return a 32-character hex string."""
        result = hash_password("test")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def testhash_password_triple_hashes(self):
        """Should apply MD5 three times."""
        password = "mypassword"

        # Manual triple hash
        expected = password
        for _ in range(3):
            expected = hashlib.md5(expected.encode()).hexdigest()

        assert hash_password(password) == expected

    def testhash_password_deterministic(self):
        """Same input should produce same output."""
        assert hash_password("test123") == hash_password("test123")


class TestToken:
    """Tests for Token dataclass."""

    def test_token_creation(self):
        """Should create token with access and refresh tokens."""
        token = Token(access_token="access", refresh_token="refresh")
        assert token.access_token == "access"
        assert token.refresh_token == "refresh"

    def test_token_should_refresh_false_when_new(self):
        """New token should not need refresh."""
        token = Token(access_token="access", refresh_token="refresh")
        assert token.should_refresh is False

    def test_token_should_refresh_true_when_old(self):
        """Old token should need refresh."""
        import time
        token = Token(
            access_token="access",
            refresh_token="refresh",
            created_at=time.time() - 90000,  # 25 hours ago
        )
        assert token.should_refresh is True


class TestWyzeapyInit:
    """Tests for Wyzeapy initialization."""

    def test_init_stores_credentials(self):
        """Should store hashed password and other credentials."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")

        assert wyze._email == "test@example.com"
        assert wyze._password_hash == hash_password("password")
        assert wyze._key_id == "key_id"
        assert wyze._api_key == "api_key"

    def test_init_generates_phone_id(self):
        """Should generate a UUID for phone_id."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")

        assert wyze._phone_id is not None
        assert len(wyze._phone_id) == 36  # UUID format

    def test_init_no_token(self):
        """Should start without a token."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")
        assert wyze._token is None

    def test_init_no_clients(self):
        """Should start without HTTP clients."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")
        assert wyze._auth_client is None
        assert wyze._main_client is None

    def test_init_with_tfa_callback(self):
        """Should store 2FA callback."""
        callback = lambda auth_type: "123456"
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key", tfa_callback=callback)
        assert wyze._tfa_callback is callback


class TestWyzeapyCommonParams:
    """Tests for common request parameters."""

    def test_common_params_structure(self):
        """Should return dict with all required fields."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")
        wyze._token = Token(access_token="test_token", refresh_token="refresh")

        params = wyze._common_params()

        assert "phone_system_type" in params
        assert "app_version" in params
        assert "app_ver" in params
        assert "app_name" in params
        assert "phone_id" in params
        assert "sc" in params
        assert "sv" in params
        assert "ts" in params
        assert "access_token" in params

    def test_common_params_includes_token(self):
        """Should include access token when authenticated."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")
        wyze._token = Token(access_token="my_access_token", refresh_token="refresh")

        params = wyze._common_params()
        assert params["access_token"] == "my_access_token"

    def test_common_params_raises_when_unauthenticated(self):
        """Should raise NotAuthenticatedError when not authenticated."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")

        with pytest.raises(NotAuthenticatedError):
            wyze._common_params()


@pytest.mark.integration
@pytest.mark.asyncio(loop_scope="module")
class TestWyzeapyIntegration:
    """Integration tests requiring real credentials.

    Uses a shared wyze_client fixture to avoid rate limiting from multiple logins.
    """

    async def test_list_devices_without_login_raises(self):
        """Should raise error when listing devices without login."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")

        with pytest.raises(NotAuthenticatedError, match="Not authenticated"):
            await wyze.list_devices()

    async def test_list_devices(self, wyze_client):
        """Should list devices."""
        devices = await wyze_client.list_devices()

        assert isinstance(devices, list)
        print(f"\nFound {len(devices)} devices:")
        for device in devices:
            print(f"  - {device.nickname} ({device.product_model})")

    async def test_get_user(self, wyze_client):
        """Should retrieve user profile."""
        user = await wyze_client.get_user()

        assert isinstance(user, WyzeUser)
        assert user.user_id is not None
        print(f"\nUser: {user.nickname} (ID: {user.user_id})")

    async def test_devices_have_required_attributes(self, wyze_client):
        """All devices should have required base attributes."""
        devices = await wyze_client.list_devices()

        for device in devices:
            assert isinstance(device, WyzeDevice)
            assert device.mac is not None
            assert device.nickname is not None
            assert device.product_model is not None
            assert isinstance(device.type, DeviceType)
            assert isinstance(device.available, bool)

    async def test_devices_correctly_typed(self, wyze_client):
        """Devices should be instantiated as correct subclass types."""
        devices = await wyze_client.list_devices()

        type_mapping = {
            DeviceType.CAMERA: WyzeCamera,
            DeviceType.PLUG: WyzePlug,
            DeviceType.LOCK: WyzeLock,
            DeviceType.LIGHT: WyzeLight,
            DeviceType.THERMOSTAT: WyzeThermostat,
            DeviceType.CONTACT_SENSOR: WyzeSensor,
            DeviceType.MOTION_SENSOR: WyzeSensor,
            DeviceType.LEAK_SENSOR: WyzeSensor,
        }

        for device in devices:
            if device.type in type_mapping:
                expected_class = type_mapping[device.type]
                assert isinstance(device, expected_class), (
                    f"{device.nickname} has type {device.type} but is "
                    f"{type(device).__name__}, expected {expected_class.__name__}"
                )

    async def test_list_devices_caching(self, wyze_client):
        """Second call to list_devices should use cache."""
        # Note: refresh=True tests removed due to pytest-asyncio/httpx event loop issues
        devices1 = await wyze_client.list_devices()
        devices2 = await wyze_client.list_devices()  # Should use cache

        # Same objects should be returned from cache
        assert devices1 is devices2

    # Note: Device-specific operation tests (camera, plug, lock, thermostat)
    # have been removed due to pytest-asyncio/httpx event loop compatibility
    # issues. The device classes and their methods are tested manually via
    # example.py or src/wyzeapy/tests/test_get_user.py