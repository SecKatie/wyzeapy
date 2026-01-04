from enum import Enum


class ThermostatIotPropResponseDataPropsModeSys(str, Enum):
    AUTO = "auto"
    COOL = "cool"
    HEAT = "heat"
    OFF = "off"

    def __str__(self) -> str:
        return str(self.value)
