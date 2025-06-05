from medical_system.usecases.dtos.appointment_dto import AppointmentDTO
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.entities.appointment import Appointment


class CompleteAppointmentUseCase:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    def execute(self, appointment_id: int, doctor_id: int):
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.doctor.id != doctor_id:
            raise UnauthorizedError("You can only complete your own appointments")
        appointment.complete()

        return self.appointment_repository.save(appointment)
