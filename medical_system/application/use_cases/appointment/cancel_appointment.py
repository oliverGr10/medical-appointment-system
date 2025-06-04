from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.application.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.entities.appointment import Appointment
from medical_system.domain.exceptions import UnauthorizedError


class CancelAppointmentUseCase:
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: PatientRepository,
    ):
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository

    def execute(self, appointment_id: int, patient_id: int) -> None:
        # Get the appointment
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        # Verify the patient owns the appointment
        if appointment.patient.id != patient_id:
            raise UnauthorizedError("You can only cancel your own appointments")

        # Cancel the appointment
        appointment.cancel()
        
        # Save the updated appointment
        self.appointment_repository.save(appointment)
