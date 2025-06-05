from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.exceptions import UnauthorizedError

class CancelAppointmentUseCase:

    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: PatientRepository,
    ):

        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository

    def execute(self, appointment_id: int, patient_id: int):

        appointment = self.appointment_repository.find_by_id(appointment_id)      
        if not appointment:
            raise ValueError("No se encontró la cita especificada")

        if appointment.patient.id != patient_id:
            raise UnauthorizedError("Solo puedes cancelar tus propias citas")

        appointment.cancel()

        updated_appointment = self.appointment_repository.save(appointment)
        
        return updated_appointment
