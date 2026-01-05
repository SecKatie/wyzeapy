from enum import Enum


class SendSmsCodeBodyMfaPhoneType(str, Enum):
    PRIMARY = "Primary"

    def __str__(self) -> str:
        return str(self.value)
