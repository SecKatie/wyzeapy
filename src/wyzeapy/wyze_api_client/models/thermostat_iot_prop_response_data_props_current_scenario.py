from enum import Enum


class ThermostatIotPropResponseDataPropsCurrentScenario(str, Enum):
    AWAY = "away"
    HOME = "home"
    SLEEP = "sleep"

    def __str__(self) -> str:
        return str(self.value)
