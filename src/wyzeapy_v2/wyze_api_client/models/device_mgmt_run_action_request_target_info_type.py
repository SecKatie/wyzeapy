from enum import Enum


class DeviceMgmtRunActionRequestTargetInfoType(str, Enum):
    DEVICE = "DEVICE"

    def __str__(self) -> str:
        return str(self.value)
