from enum import Enum


class SetPushInfoRequestPushSwitch(str, Enum):
    VALUE_0 = "1"
    VALUE_1 = "2"

    def __str__(self) -> str:
        return str(self.value)
