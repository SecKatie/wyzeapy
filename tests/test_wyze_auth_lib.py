import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from wyzeapy.wyze_auth_lib import WyzeAuthLib, Token, TwoFactorAuthenticationEnabled, AccessTokenError, UnknownApiError
from wyzeapy.types import ResponseCodes # Import ResponseCodes
import asyncio
import time
import aiohttp # Import aiohttp

class TestWyzeAuthLib(unittest.IsolatedAsyncioTestCase):

    def test_initialization(self):
        auth_lib = WyzeAuthLib(username='test_user', password='test_password')
        self.assertEqual(auth_lib._username, 'test_user')
        self.assertEqual(auth_lib._password, 'test_password')

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_login_success(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }
        # The session context manager returns an object that has an async post method
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        # Mock the token_callback
        mock_token_callback = AsyncMock()

        auth_lib = WyzeAuthLib(username='test_user', password='test_password', token_callback=mock_token_callback)
        token = await auth_lib.get_token_with_username_password('test_user', 'test_password', 'test_key_id', 'test_api_key')

        self.assertIsInstance(token, Token)
        mock_token_callback.assert_called_once_with(token)

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_2fa_sms(self, mock_session):
        # First response indicates 2FA is needed
        mock_2fa_response = AsyncMock()
        mock_2fa_response.json.return_value = {
            "mfa_options": ["PrimaryPhone"],
            "sms_session_id": "some_session_id",
            "user_id": "some_user_id"
        }
        # Second response for sending the code
        mock_sms_sent_response = AsyncMock()
        mock_sms_sent_response.json.return_value = {
            "session_id": "some_new_session_id"
        }

        # Set up the mock session to return the responses in order
        mock_session.return_value.__aenter__.return_value.post.side_effect = [
            mock_2fa_response,
            mock_sms_sent_response
        ]

        auth_lib = WyzeAuthLib(username='test_user', password='test_password')

        with self.assertRaises(TwoFactorAuthenticationEnabled):
            await auth_lib.get_token_with_username_password('test_user', 'test_password', 'test_key_id', 'test_api_key')

        self.assertEqual(auth_lib.two_factor_type, "SMS")
        self.assertEqual(auth_lib.session_id, "some_new_session_id")

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_2fa_totp(self, mock_session):
        # First response indicates 2FA is needed
        mock_2fa_response = AsyncMock()
        mock_2fa_response.json.return_value = {
            "mfa_options": ["TotpVerificationCode"],
            "mfa_details": {
                "totp_apps": [
                    {"app_id": "some_app_id"}
                ]
            }
        }

        # Set up the mock session to return the responses in order
        mock_session.return_value.__aenter__.return_value.post.side_effect = [
            mock_2fa_response
        ]

        auth_lib = WyzeAuthLib(username='test_user', password='test_password')

        with self.assertRaises(TwoFactorAuthenticationEnabled):
            await auth_lib.get_token_with_username_password('test_user', 'test_password', 'test_key_id', 'test_api_key')

        self.assertEqual(auth_lib.two_factor_type, "TOTP")
        self.assertEqual(auth_lib.verification_id, "some_app_id")

    def test_token_properties(self):
        initial_access = "initial_access"
        initial_refresh = "initial_refresh"
        token = Token(initial_access, initial_refresh)

        self.assertEqual(token.access_token, initial_access)
        self.assertEqual(token.refresh_token, initial_refresh)
        self.assertGreater(token.refresh_time, time.time())

        new_access = "new_access"
        token.access_token = new_access
        self.assertEqual(token.access_token, new_access)
        self.assertGreater(token.refresh_time, time.time()) # Should reset refresh_time

        new_refresh = "new_refresh"
        token.refresh_token = new_refresh
        self.assertEqual(token.refresh_token, new_refresh)

        token.expired = True
        self.assertTrue(token.expired)

    async def test_create_no_credentials_or_token(self):
        with self.assertRaises(AttributeError):
            await WyzeAuthLib.create()

    async def test_create_with_credentials(self):
        auth_lib = await WyzeAuthLib.create(username='test_user', password='test_password')
        self.assertEqual(auth_lib._username, 'test_user')
        self.assertEqual(auth_lib._password, 'test_password')

    async def test_create_with_token(self):
        mock_token = Token("access", "refresh")
        auth_lib = await WyzeAuthLib.create(token=mock_token)
        self.assertEqual(auth_lib.token, mock_token)

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_login_access_token_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'errorCode': 1000,
            'msg': 'Access Token Error'
        }
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        auth_lib = WyzeAuthLib(username='test_user', password='test_password')
        with self.assertRaises(AccessTokenError):
            await auth_lib.get_token_with_username_password('test_user', 'test_password', 'test_key_id', 'test_api_key')

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_login_unknown_api_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'errorCode': 9999,
            'msg': 'Unknown Error'
        }
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        auth_lib = WyzeAuthLib(username='test_user', password='test_password')
        with self.assertRaises(UnknownApiError):
            await auth_lib.get_token_with_username_password('test_user', 'test_password', 'test_key_id', 'test_api_key')

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    @patch('wyzeapy.wyze_auth_lib.check_for_errors_standard')
    async def test_refresh_success(self, mock_check_for_errors_standard, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'code': 1, # ResponseCodes.SUCCESS.value
            'data': {
                'access_token': 'new_access',
                'refresh_token': 'new_refresh'
            }
        }
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        mock_token = Token("old_access", "old_refresh", refresh_time=time.time() - 100) # Expired
        mock_token_callback = AsyncMock()
        auth_lib = WyzeAuthLib(token=mock_token, token_callback=mock_token_callback)

        await auth_lib.refresh()

        self.assertEqual(auth_lib.token.access_token, 'new_access')
        self.assertEqual(auth_lib.token.refresh_token, 'new_refresh')
        self.assertFalse(auth_lib.token.expired)
        mock_token_callback.assert_called_once_with(auth_lib.token)
        mock_check_for_errors_standard.assert_called_once()

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    @patch('wyzeapy.wyze_auth_lib.check_for_errors_standard')
    async def test_refresh_access_token_error(self, mock_check_for_errors_standard, mock_session):
        def custom_side_effect(service, response_json):
            service.token.expired = True
            raise AccessTokenError("2001", "Refresh Token Error")
        mock_check_for_errors_standard.side_effect = custom_side_effect

        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'code': "2001", # Access Token Error
            'msg': 'Refresh Token Error'
        }
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        mock_token = Token("old_access", "old_refresh", refresh_time=time.time() - 100)
        auth_lib = WyzeAuthLib(token=mock_token)

        with self.assertRaises(AccessTokenError):
            await auth_lib.refresh()
        self.assertTrue(auth_lib.token.expired)
        mock_check_for_errors_standard.assert_called_once()

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    @patch('wyzeapy.wyze_auth_lib.check_for_errors_standard', side_effect=UnknownApiError)
    async def test_refresh_unknown_api_error(self, mock_check_for_errors_standard, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'code': 9999,
            'msg': 'Unknown Refresh Error'
        }
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        mock_token = Token("old_access", "old_refresh", refresh_time=time.time() - 100)
        auth_lib = WyzeAuthLib(token=mock_token)

        with self.assertRaises(UnknownApiError):
            await auth_lib.refresh()
        mock_check_for_errors_standard.assert_called_once()

    async def test_refresh_if_should_true(self):
        mock_token = Token("access", "refresh", refresh_time=time.time() - 100) # Expired
        auth_lib = WyzeAuthLib(token=mock_token)
        auth_lib.refresh = AsyncMock() # Mock the refresh method

        await auth_lib.refresh_if_should()
        auth_lib.refresh.assert_awaited_once()

    async def test_refresh_if_should_expired_true(self):
        mock_token = Token("access", "refresh")
        mock_token.expired = True
        auth_lib = WyzeAuthLib(token=mock_token)
        auth_lib.refresh = AsyncMock()

        await auth_lib.refresh_if_should()
        auth_lib.refresh.assert_awaited_once()

    async def test_refresh_if_should_false(self):
        mock_token = Token("access", "refresh", refresh_time=time.time() + 1000) # Not expired
        auth_lib = WyzeAuthLib(token=mock_token)
        auth_lib.refresh = AsyncMock()

        await auth_lib.refresh_if_should()
        auth_lib.refresh.assert_not_awaited()

    def test_sanitize(self):
        auth_lib = WyzeAuthLib()
        data = {
            "email": "test@example.com",
            "password": "mysecretpassword",
            "access_token": "some_access_token",
            "nested": {
                "refresh_token": "some_refresh_token",
                "non_sensitive": "value"
            },
            "non_sensitive_top": "another_value"
        }
        sanitized_data = auth_lib.sanitize(data)

        self.assertEqual(sanitized_data["email"], auth_lib.SANITIZE_STRING)
        self.assertEqual(sanitized_data["password"], auth_lib.SANITIZE_STRING)
        self.assertEqual(sanitized_data["access_token"], auth_lib.SANITIZE_STRING)
        self.assertEqual(sanitized_data["nested"]["refresh_token"], auth_lib.SANITIZE_STRING)
        self.assertEqual(sanitized_data["nested"]["non_sensitive"], "value")
        self.assertEqual(sanitized_data["non_sensitive_top"], "another_value")

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_post_success(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        auth_lib = WyzeAuthLib()
        result = await auth_lib.post("http://test.com", json={"key": "value"})
        self.assertEqual(result, {"status": "success"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_put_success(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.__aenter__.return_value.put.return_value = mock_response

        auth_lib = WyzeAuthLib()
        result = await auth_lib.put("http://test.com", json={"key": "value"})
        self.assertEqual(result, {"status": "success"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_get_success(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

        auth_lib = WyzeAuthLib()
        result = await auth_lib.get("http://test.com", params={"key": "value"})
        self.assertEqual(result, {"status": "success"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_patch_success(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.__aenter__.return_value.patch.return_value = mock_response

        auth_lib = WyzeAuthLib()
        result = await auth_lib.patch("http://test.com", json={"key": "value"})
        self.assertEqual(result, {"status": "success"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_delete_success(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.__aenter__.return_value.delete.return_value = mock_response

        auth_lib = WyzeAuthLib()
        result = await auth_lib.delete("http://test.com", json={"key": "value"})
        self.assertEqual(result, {"status": "success"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_post_content_type_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.side_effect = aiohttp.ContentTypeError(
            request_info=MagicMock(),
            history=(),
            message="Not JSON",
            headers=MagicMock()
        )
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        auth_lib = WyzeAuthLib()
        with self.assertRaises(aiohttp.ContentTypeError):
            await auth_lib.post("http://test.com", json={"key": "value"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_put_content_type_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.side_effect = aiohttp.ContentTypeError(
            request_info=MagicMock(),
            history=(),
            message="Not JSON",
            headers=MagicMock()
        )
        mock_session.return_value.__aenter__.return_value.put.return_value = mock_response

        auth_lib = WyzeAuthLib()
        with self.assertRaises(aiohttp.ContentTypeError):
            await auth_lib.put("http://test.com", json={"key": "value"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_get_content_type_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.side_effect = aiohttp.ContentTypeError(
            request_info=MagicMock(),
            history=(),
            message="Not JSON",
            headers=MagicMock()
        )
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

        auth_lib = WyzeAuthLib()
        with self.assertRaises(aiohttp.ContentTypeError):
            await auth_lib.get("http://test.com", params={"key": "value"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_patch_content_type_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.side_effect = aiohttp.ContentTypeError(
            request_info=MagicMock(),
            history=(),
            message="Not JSON",
            headers=MagicMock()
        )
        mock_session.return_value.__aenter__.return_value.patch.return_value = mock_response

        auth_lib = WyzeAuthLib()
        with self.assertRaises(aiohttp.ContentTypeError):
            await auth_lib.patch("http://test.com", json={"key": "value"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_delete_content_type_error(self, mock_session):
        mock_response = AsyncMock()
        mock_response.json.side_effect = aiohttp.ContentTypeError(
            request_info=MagicMock(),
            history=(),
            message="Not JSON",
            headers=MagicMock()
        )
        mock_session.return_value.__aenter__.return_value.delete.return_value = mock_response

        auth_lib = WyzeAuthLib()
        with self.assertRaises(aiohttp.ContentTypeError):
            await auth_lib.delete("http://test.com", json={"key": "value"})

    @patch('wyzeapy.wyze_auth_lib.ClientSession')
    async def test_get_token_with_2fa_sms_success(self, mock_session):
        # Mock the initial login response to indicate SMS 2FA is required
        mock_login_response = AsyncMock()
        mock_login_response.json.return_value = {
            "mfa_options": ["PrimaryPhone"],
            "sms_session_id": "initial_session_id",
            "user_id": "test_user_id"
        }
        # Mock the 2FA verification response
        mock_2fa_verify_response = AsyncMock()
        mock_2fa_verify_response.json.return_value = {
            'access_token': 'verified_access_token',
            'refresh_token': 'verified_refresh_token'
        }

        # Second response for sending the code
        mock_sms_sent_response = AsyncMock()
        mock_sms_sent_response.json.return_value = {
            "session_id": "some_new_session_id"
        }

        # Set up the mock session to return responses for all calls
        mock_session.return_value.__aenter__.return_value.post.side_effect = [
            mock_login_response,  # First post call in get_token_with_username_password
            mock_sms_sent_response, # Second post call in get_token_with_username_password
            mock_2fa_verify_response  # Post call in get_token_with_2fa
        ]

        mock_token_callback = AsyncMock()
        auth_lib = WyzeAuthLib(username='test_user', password='test_password', token_callback=mock_token_callback)

        # Simulate the initial login call that triggers 2FA
        with self.assertRaises(TwoFactorAuthenticationEnabled):
            await auth_lib.get_token_with_username_password('test_user', 'test_password', 'test_key_id', 'test_api_key')

        # Now call get_token_with_2fa
        token = await auth_lib.get_token_with_2fa('123456')

        self.assertIsInstance(token, Token)
        self.assertEqual(token.access_token, auth_lib.SANITIZE_STRING)
        self.assertEqual(token.refresh_token, auth_lib.SANITIZE_STRING)
        mock_token_callback.assert_called_once_with(token)