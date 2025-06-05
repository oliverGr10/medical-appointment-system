from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateDoctorDTO:
    name: str
    email: str
    specialty: str

@dataclass
class UpdateDoctorDTO:
    name: Optional[str] = None
    email: Optional[str] = None
    specialty: Optional[str] = None

@dataclass
class DoctorDTO:
    id: int
    name: str
    email: str
    specialty: str
