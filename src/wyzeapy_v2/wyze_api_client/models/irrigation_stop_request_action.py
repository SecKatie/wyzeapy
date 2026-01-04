from enum import Enum


class IrrigationStopRequestAction(str, Enum):
    STOP = "STOP"

    def __str__(self) -> str:
        return str(self.value)
