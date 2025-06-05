from dataclasses import dataclass
from datetime import date, time, datetime
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
        appointment_datetime = datetime.combine(self.date, self.time)
        if appointment_datetime <= datetime.now():
            raise ValueError("La cita debe ser en el futuro")
        
        if not (time(8, 0) <= self.time < time(20, 0)):
            raise ValueError("La cita debe estar entre las 8:00 y las 20:00 horas")
        
        if self.time.minute % 30 != 0:
            raise ValueError("La hora de la cita debe ser en intervalos de 30 minutos")

    def cancel(self):
        if self.status == AppointmentStatus.CANCELLED:
            raise ValueError("La cita ya está cancelada")
        if self.status == AppointmentStatus.COMPLETED:
            raise ValueError("No se puede cancelar una cita completada")
        self.status = AppointmentStatus.CANCELLED

    def complete(self):
        if self.status == AppointmentStatus.CANCELLED:
            raise ValueError("No se puede completar una cita cancelada")
        if self.status == AppointmentStatus.COMPLETED:
            raise ValueError("La cita ya está completada")
        self.status = AppointmentStatus.COMPLETED
