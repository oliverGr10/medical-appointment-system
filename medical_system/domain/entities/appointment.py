from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional

from medical_system.domain.entities.base_entity import BaseEntity
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.patient import Patient
from medical_system.domain.value_objects.reservation_status import AppointmentStatus


@dataclass
class Appointment(BaseEntity):
    date: date
    time: time
    status: AppointmentStatus
    patient: Patient
    doctor: Doctor

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        # Validate appointment is in the future
        appointment_datetime = datetime.combine(self.date, self.time)
        if appointment_datetime <= datetime.now():
            raise ValueError("Appointment must be in the future")
        
        # Validate working hours (8am to 8pm)
        if not (time(8, 0) <= self.time < time(20, 0)):
            raise ValueError("Appointment must be between 8:00 and 20:00")
        
        # Round to nearest 30 minutes
        if self.time.minute % 30 != 0:
            raise ValueError("Appointment time must be at 30-minute intervals")

    def cancel(self):
        if self.status == AppointmentStatus.CANCELLED:
            raise ValueError("Appointment is already cancelled")
        if self.status == AppointmentStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed appointment")
        self.status = AppointmentStatus.CANCELLED

    def complete(self):
        if self.status == AppointmentStatus.CANCELLED:
            raise ValueError("Cannot complete a cancelled appointment")
        if self.status == AppointmentStatus.COMPLETED:
            raise ValueError("Appointment is already completed")
        self.status = AppointmentStatus.COMPLETED
