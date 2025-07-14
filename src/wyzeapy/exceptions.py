#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy
"""
Custom exception classes for Wyzeapy API interactions.
"""

class ActionNotSupported(Exception):
    """Raised when an unsupported action is requested for a device type."""

    def __init__(self, device_type: str):
        message = (
            f"The action specified is not supported by device type: {device_type}"
        )
        super().__init__(message)


class ParameterError(Exception):
    """Raised when invalid parameters are provided to an API call."""


class AccessTokenError(Exception):
    """Raised when the access token is invalid or has expired."""


class LoginError(Exception):
    """Raised during authentication or login failures."""


class UnknownApiError(Exception):
    """Raised for unexpected or generic API errors."""


class TwoFactorAuthenticationEnabled(Exception):
    """Raised when two-factor authentication is required for login."""
