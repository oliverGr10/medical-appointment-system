from enum import Enum, auto


class AppointmentStatus(Enum):
    SCHEDULED = auto()
    CANCELLED = auto()
    COMPLETED = auto()

    def __str__(self) -> str:
        return self.name.lower()
