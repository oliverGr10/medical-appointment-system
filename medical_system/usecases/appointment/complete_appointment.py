from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.exceptions import UnauthorizedError

class CompleteAppointmentUseCase:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    def execute(self, appointment_id: int, doctor_id: int):
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("No se encontró la cita especificada")

        if appointment.doctor.id != doctor_id:
            raise UnauthorizedError("Solo puedes completar tus propias citas")
        appointment.complete()

        return self.appointment_repository.save(appointment)
