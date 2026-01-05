from enum import Enum


class TwoFactorLoginRequestMfaType(str, Enum):
    PRIMARYPHONE = "PrimaryPhone"
    TOTPVERIFICATIONCODE = "TotpVerificationCode"

    def __str__(self) -> str:
        return str(self.value)
