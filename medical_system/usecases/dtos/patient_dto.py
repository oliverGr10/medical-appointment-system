from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class CreatePatientDTO:
    name: str
    email: str
    birth_date: date

@dataclass
class UpdatePatientDTO:
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None

@dataclass
class PatientDTO:
    id: int
    name: str
    email: str
    birth_date: date
