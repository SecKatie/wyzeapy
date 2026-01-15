"""Wyzeapy exceptions."""


class WyzeapyError(Exception):
    """Base exception for all Wyzeapy errors."""

    pass


class AuthenticationError(WyzeapyError):
    """Raised when authentication fails."""

    pass


class TwoFactorAuthRequired(AuthenticationError):
    """
    Raised when 2FA is required but no callback provided.

    :param auth_type: Type of 2FA required (e.g., \"TOTP\" or \"SMS\").
    :type auth_type: str
    """

    def __init__(self, auth_type: str):
        self.auth_type = auth_type
        super().__init__(f"Two-factor authentication ({auth_type}) required")


class TokenRefreshError(AuthenticationError):
    """Raised when token refresh fails."""

    pass


class NotAuthenticatedError(WyzeapyError):
    """Raised when attempting to use API without authentication."""

    pass


class DeviceError(WyzeapyError):
    """Base exception for device-related errors."""

    pass


class DeviceOfflineError(DeviceError):
    """Raised when a device is offline."""

    pass


class ActionNotSupportedError(DeviceError):
    """Raised when an action is not supported by a device."""

    pass


class ActionFailedError(DeviceError):
    """
    Raised when a device action fails.

    :param action: The action that failed.
    :type action: str
    :param device_mac: The MAC address of the device.
    :type device_mac: str
    :param response: The API response, if any.
    :type response: Any
    """

    def __init__(self, action: str, device_mac: str, response: object = None):
        self.action = action
        self.device_mac = device_mac
        self.response = response
        super().__init__(f"Action '{action}' failed for device {device_mac}")


class ApiError(WyzeapyError):
    """
    Raised when the API returns an error.

    :param code: API error code.
    :type code: str
    :param message: Optional error message.
    :type message: str
    """

    def __init__(self, code: str, message: str = ""):
        self.code = code
        self.message = message
        super().__init__(
            f"API error {code}: {message}" if message else f"API error {code}"
        )
