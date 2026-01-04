from enum import Enum


class DisableRemeAlarmBodyRemediationId(str, Enum):
    EMERGENCY = "emergency"

    def __str__(self) -> str:
        return str(self.value)
