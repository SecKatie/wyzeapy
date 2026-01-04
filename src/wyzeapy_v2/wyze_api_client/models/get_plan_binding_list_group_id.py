from enum import Enum


class GetPlanBindingListGroupId(str, Enum):
    HMS = "hms"

    def __str__(self) -> str:
        return str(self.value)
