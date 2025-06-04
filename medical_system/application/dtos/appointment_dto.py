from dataclasses import dataclass
from datetime import date, time

from medical_system.application.dtos.doctor_dto import DoctorDTO
from medical_system.application.dtos.patient_dto import PatientDTO
from medical_system.domain.value_objects.reservation_status import AppointmentStatus


@dataclass
class CreateAppointmentDTO:
    patient_id: int
    doctor_id: int
    date: date
    time: time


@dataclass
class GetDoctorAppointmentsDTO:
    doctor_id: int
    date: date


@dataclass
class AppointmentDTO:
    id: int
    date: date
    time: time
    status: str
    patient: PatientDTO
    doctor: DoctorDTO
