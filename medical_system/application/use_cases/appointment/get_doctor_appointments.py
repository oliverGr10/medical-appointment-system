from datetime import date
from typing import List

from medical_system.application.dtos.appointment_dto import AppointmentDTO
from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.application.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.exceptions import UnauthorizedError


class GetDoctorAppointmentsUseCase:
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        doctor_repository: DoctorRepository,
    ):
        self.appointment_repository = appointment_repository
        self.doctor_repository = doctor_repository

    def execute(self, doctor_id: int, request_date: date, requesting_doctor_id: int) -> List[AppointmentDTO]:
        # Verify the requesting doctor is the same as the requested doctor
        if doctor_id != requesting_doctor_id:
            raise UnauthorizedError("You can only view your own appointments")

        # Verify doctor exists
        doctor = self.doctor_repository.find_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")


        # Get appointments
        appointments = self.appointment_repository.find_by_doctor_and_date(
            doctor_id=doctor_id,
            date=request_date
        )

        # Convert to DTOs
        return [self._to_dto(apt) for apt in appointments]
    
    @staticmethod
    def _to_dto(appointment) -> AppointmentDTO:
        from medical_system.application.dtos.patient_dto import PatientDTO
        from medical_system.application.dtos.doctor_dto import DoctorDTO
        
        return AppointmentDTO(
            id=appointment.id,
            date=appointment.date,
            time=appointment.time,
            status=str(appointment.status).lower(),
            patient=PatientDTO(
                id=appointment.patient.id,
                name=appointment.patient.name,
                email=str(appointment.patient.email),
                birth_date=appointment.patient.birth_date,
            ),
            doctor=DoctorDTO(
                id=appointment.doctor.id,
                name=appointment.doctor.name,
                email=str(appointment.doctor.email),
                specialty=appointment.doctor.specialty,
            ),
        )
