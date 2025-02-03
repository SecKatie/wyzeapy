#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  katie@mulliken.net to receive a copy


class ActionNotSupported(Exception):
    def __init__(self, device_type: str):
        message = "The action specified is not supported by device type: {}".format(
            device_type
        )

        super().__init__(message)


class ParameterError(Exception):
    pass


class AccessTokenError(Exception):
    pass


class LoginError(Exception):
    pass


class UnknownApiError(Exception):
    pass


class TwoFactorAuthenticationEnabled(Exception):
    pass
