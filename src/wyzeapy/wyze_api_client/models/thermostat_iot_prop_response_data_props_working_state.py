from enum import Enum


class ThermostatIotPropResponseDataPropsWorkingState(str, Enum):
    COOLING = "cooling"
    HEATING = "heating"
    IDLE = "idle"

    def __str__(self) -> str:
        return str(self.value)
