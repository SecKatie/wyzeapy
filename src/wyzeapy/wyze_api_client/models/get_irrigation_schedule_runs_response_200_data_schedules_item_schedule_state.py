from enum import Enum


class GetIrrigationScheduleRunsResponse200DataSchedulesItemScheduleState(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
