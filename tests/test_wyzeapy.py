"""Tests for the Wyzeapy wrapper."""

import hashlib
import pytest

from src.wyzeapy import Wyzeapy, Token
from src.wyzeapy.wyzeapy import _hash_password


class TestHashPassword:
    """Tests for password hashing."""

    def test_hash_password_returns_md5(self):
        """Should return a 32-character hex string."""
        result = _hash_password("test")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_password_triple_hashes(self):
        """Should apply MD5 three times."""
        password = "mypassword"

        # Manual triple hash
        expected = password
        for _ in range(3):
            expected = hashlib.md5(expected.encode()).hexdigest()

        assert _hash_password(password) == expected

    def test_hash_password_deterministic(self):
        """Same input should produce same output."""
        assert _hash_password("test123") == _hash_password("test123")


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
        assert wyze._password_hash == _hash_password("password")
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

    def test_common_params_empty_token_when_unauthenticated(self):
        """Should have empty access token when not authenticated."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")

        params = wyze._common_params()
        assert params["access_token"] == ""


@pytest.mark.integration
class TestWyzeapyIntegration:
    """Integration tests requiring real credentials."""

    @pytest.mark.asyncio
    async def test_login_and_list_devices(self, wyze_credentials):
        """Should login and list devices."""
        async with Wyzeapy(
            wyze_credentials["email"],
            wyze_credentials["password"],
            wyze_credentials["key_id"],
            wyze_credentials["api_key"],
        ) as wyze:
            devices = await wyze.list_devices()

            assert isinstance(devices, list)
            print(f"\nFound {len(devices)} devices:")
            for device in devices:
                print(f"  - {device.nickname} ({device.product_model})")

    @pytest.mark.asyncio
    async def test_list_devices_without_login_raises(self):
        """Should raise error when listing devices without login."""
        wyze = Wyzeapy("test@example.com", "password", "key_id", "api_key")

        with pytest.raises(RuntimeError, match="Not authenticated"):
            await wyze.list_devices()

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self, wyze_credentials):
        """Should clean up clients on exit."""
        wyze = Wyzeapy(
            wyze_credentials["email"],
            wyze_credentials["password"],
            wyze_credentials["key_id"],
            wyze_credentials["api_key"],
        )

        async with wyze:
            # Force client creation
            _ = wyze._get_auth_client()
            _ = wyze._get_main_client()

            assert wyze._auth_client is not None
            assert wyze._main_client is not None

        # After exit, clients should be closed (not None, but closed)
        # We can't easily test closed state, but verify no exceptions