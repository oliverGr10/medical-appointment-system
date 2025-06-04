from medical_system.application.dtos.appointment_dto import AppointmentDTO
from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.entities.appointment import Appointment


class CompleteAppointmentUseCase:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    def execute(self, appointment_id: int, doctor_id: int) -> AppointmentDTO:
        # Get the appointment
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        # Verify the doctor owns the appointment
        if appointment.doctor.id != doctor_id:
            raise UnauthorizedError("You can only complete your own appointments")

        # Mark as completed
        appointment.complete()
        
        # Save the updated appointment
        updated_appointment = self.appointment_repository.save(appointment)
        
        # Return the DTO
        return self._to_dto(updated_appointment)
    
    @staticmethod
    def _to_dto(appointment: Appointment) -> AppointmentDTO:
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
