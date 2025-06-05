from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "Programada"
    CANCELLED = "Cancelada"
    COMPLETED = "Completada"

    def __str__(self) -> str:
        return self.value

