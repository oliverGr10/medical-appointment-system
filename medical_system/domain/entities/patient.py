from dataclasses import dataclass
from datetime import date
from medical_system.domain.entities.base_entity import BaseEntity
from medical_system.domain.value_objects.email import Email

@dataclass
class Patient(BaseEntity):
    name: str
    email: Email
    birth_date: date

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if self.birth_date >= date.today():
            raise ValueError("Birth date must be in the past")
