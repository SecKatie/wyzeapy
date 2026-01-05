from enum import Enum


class WallSwitchIotPropResponseDataPropsIotState(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

    def __str__(self) -> str:
        return str(self.value)
