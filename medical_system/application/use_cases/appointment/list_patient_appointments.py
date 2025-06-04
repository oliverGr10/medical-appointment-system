from typing import List

from medical_system.application.dtos.appointment_dto import AppointmentDTO
from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.application.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.exceptions import UnauthorizedError


class ListPatientAppointmentsUseCase:
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: PatientRepository,
    ):
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository

    def execute(self, patient_id: int, requesting_patient_id: int) -> List[AppointmentDTO]:
        # Verify the requesting patient is the same as the requested patient
        if patient_id != requesting_patient_id:
            raise UnauthorizedError("You can only view your own appointments")

        # Verify patient exists
        patient = self.patient_repository.find_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Get appointments
        appointments = self.appointment_repository.find_by_patient(patient_id)
        
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
