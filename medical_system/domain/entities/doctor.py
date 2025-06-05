from dataclasses import dataclass
from medical_system.domain.entities.base_entity import BaseEntity
from medical_system.domain.value_objects.email import Email

@dataclass
class Doctor(BaseEntity):
    name: str
    email: Email
    specialty: str

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        
        if not self.specialty or len(self.specialty.strip()) < 2:
            raise ValueError("Specialty must be at least 2 characters long")
