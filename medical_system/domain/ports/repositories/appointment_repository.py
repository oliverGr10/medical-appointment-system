from abc import ABC, abstractmethod
from datetime import date, datetime, time
from typing import List, Optional

from medical_system.domain.entities.appointment import Appointment

class AppointmentRepository(ABC):
    @abstractmethod
    def find_by_id(self, appointment_id: int) -> Optional[Appointment]:
        raise NotImplementedError

    @abstractmethod
    def save(self, appointment: Appointment) -> Appointment:
        raise NotImplementedError

    @abstractmethod
    def find_by_doctor_and_date(
        self, doctor_id: int, date: date
    ) -> List[Appointment]:
        raise NotImplementedError

    @abstractmethod
    def find_by_patient(self, patient_id: int) -> List[Appointment]:
        raise NotImplementedError
        
    @abstractmethod
    def find_by_patient_and_date(
        self, patient_id: int, date: date
    ) -> List[Appointment]:
        raise NotImplementedError

    @abstractmethod
    def find_available_slots(
        self, doctor_id: int, date: date
    ) -> List[datetime]:
        raise NotImplementedError
        
    @abstractmethod
    def find_by_doctor_patient_datetime(
        self, doctor_id: int, patient_id: int, date: date, time: time
    ) -> Optional[Appointment]:
        raise NotImplementedError
        
    @abstractmethod
    def find_patient_appointments_at_same_time(
        self, patient_id: int, date: date, time: time
    ) -> List[Appointment]:
        raise NotImplementedError
        
    @abstractmethod
    def find_all(self) -> List[Appointment]:
        raise NotImplementedError
        
    @abstractmethod
    def delete(self, appointment_id: int) -> None:
        raise NotImplementedError
