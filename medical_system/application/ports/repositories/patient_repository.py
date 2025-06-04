from abc import ABC, abstractmethod
from typing import List, Optional

from medical_system.domain.entities.patient import Patient


class PatientRepository(ABC):
    @abstractmethod
    def find_by_id(self, patient_id: int) -> Optional[Patient]:
        raise NotImplementedError

    @abstractmethod
    def save(self, patient: Patient) -> Patient:
        raise NotImplementedError
        
    @abstractmethod
    def update(self, patient: Patient) -> Patient:
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Patient]:
        raise NotImplementedError
        
    @abstractmethod
    def find_all(self) -> List[Patient]:
        raise NotImplementedError
