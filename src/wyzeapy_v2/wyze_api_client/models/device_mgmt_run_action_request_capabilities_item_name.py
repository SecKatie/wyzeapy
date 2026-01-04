from enum import Enum


class DeviceMgmtRunActionRequestCapabilitiesItemName(str, Enum):
    FLOODLIGHT = "floodlight"
    IOT_DEVICE = "iot-device"
    SIREN = "siren"
    SPOTLIGHT = "spotlight"

    def __str__(self) -> str:
        return str(self.value)
