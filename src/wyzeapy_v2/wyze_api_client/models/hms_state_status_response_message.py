from enum import Enum


class HMSStateStatusResponseMessage(str, Enum):
    AWAY = "away"
    CHANGING = "changing"
    DISARM = "disarm"
    HOME = "home"

    def __str__(self) -> str:
        return str(self.value)
