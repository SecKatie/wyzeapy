from enum import Enum


class HMSProfileActiveRequestItemState(str, Enum):
    AWAY = "away"
    HOME = "home"

    def __str__(self) -> str:
        return str(self.value)
