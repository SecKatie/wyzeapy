from enum import Enum


class LockControlRequestAction(str, Enum):
    REMOTELOCK = "remoteLock"
    REMOTEUNLOCK = "remoteUnlock"

    def __str__(self) -> str:
        return str(self.value)
