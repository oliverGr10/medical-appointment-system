from typing import List

from medical_system.application.dtos.appointment_dto import AppointmentDTO
from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository


class ListAllAppointmentsUseCase:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    def execute(self) -> List[AppointmentDTO]:
        # In a real app, we would verify admin role here
        appointments = self.appointment_repository.find_all()
        
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
