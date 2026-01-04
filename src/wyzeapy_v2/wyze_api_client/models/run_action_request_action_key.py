from enum import Enum


class RunActionRequestActionKey(str, Enum):
    GARAGE_DOOR_TRIGGER = "garage_door_trigger"
    POWER_OFF = "power_off"
    POWER_ON = "power_on"
    SIREN_OFF = "siren_off"
    SIREN_ON = "siren_on"

    def __str__(self) -> str:
        return str(self.value)
