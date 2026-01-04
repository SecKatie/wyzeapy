from enum import Enum


class ThermostatIotPropResponseDataPropsFanMode(str, Enum):
    AUTO = "auto"
    ON = "on"

    def __str__(self) -> str:
        return str(self.value)
