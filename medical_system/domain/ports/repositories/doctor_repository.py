from abc import ABC, abstractmethod
from typing import List, Optional
from medical_system.domain.entities.doctor import Doctor

class DoctorRepository(ABC):
    @abstractmethod
    def find_by_id(self, doctor_id: int) -> Optional[Doctor]:
        raise NotImplementedError

    @abstractmethod
    def find_by_specialty(self, specialty: str) -> List[Doctor]:
        raise NotImplementedError
        
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Doctor]:
        raise NotImplementedError

    @abstractmethod
    def save(self, doctor: Doctor) -> Doctor:
        raise NotImplementedError
        
    @abstractmethod
    def update(self, doctor: Doctor) -> Doctor:
        raise NotImplementedError
        
    @abstractmethod
    def find_all(self) -> List[Doctor]:
        raise NotImplementedError
