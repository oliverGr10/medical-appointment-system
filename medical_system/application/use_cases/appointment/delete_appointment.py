from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.exceptions import UnauthorizedError


class DeleteAppointmentUseCase:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    def execute(self, appointment_id: int, is_admin: bool = False) -> None:
        # In a real app, we would verify admin role here
        if not is_admin:
            raise UnauthorizedError("Only administrators can delete appointments")
            
        # Verify appointment exists
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
            
        # Delete the appointment
        self.appointment_repository.delete(appointment_id)
