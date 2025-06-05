from typing import Optional
import logging
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.user_repository import UserRepository
from medical_system.domain.exceptions import (
    UnauthorizedError, 
    ResourceNotFoundError,
    BusinessRuleViolationError
)
from medical_system.domain.entities.appointment import AppointmentStatus

logger = logging.getLogger(__name__)


class DeleteAppointmentUseCase:

    def __init__(
        self, 
        appointment_repository: AppointmentRepository,
        user_repository: Optional[UserRepository] = None
    ):
        self.appointment_repository = appointment_repository
        self.user_repository = user_repository

    def execute(
        self, 
        appointment_id: int, 
        requesting_user_id: int,
        reason: Optional[str] = None,
        is_admin: bool = False
    ) -> None:

        logger.info(
            f"Iniciando eliminación de cita {appointment_id} "
            f"solicitada por usuario {requesting_user_id}"
        )
        
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            logger.warning(f"Cita {appointment_id} no encontrada")
            raise ResourceNotFoundError("La cita especificada no existe")
        
        self._check_permissions(appointment, requesting_user_id, is_admin)
        self._validate_appointment_can_be_deleted(appointment)
        
        try:
            logger.info(
                f"Eliminando cita {appointment_id} "
                f"(Paciente: {appointment.patient.id}, "
                f"Doctor: {appointment.doctor.id}, "
                f"Fecha: {appointment.date} {appointment.time})"
            )
            
            self.appointment_repository.delete(appointment_id)
            
            logger.info(f"Cita {appointment_id} eliminada exitosamente")
            
        except Exception as e:
            logger.error(
                f"Error al eliminar la cita {appointment_id}: {str(e)}", 
                exc_info=True
            )
            raise
    
    def _check_permissions(
        self, 
        appointment, 
        requesting_user_id: int, 
        is_admin: bool
    ) -> None:

        if is_admin:
            return
            
        is_doctor = (
            hasattr(appointment.doctor, 'id') and 
            appointment.doctor.id == requesting_user_id
        )
        is_patient = (
            hasattr(appointment.patient, 'id') and 
            appointment.patient.id == requesting_user_id
        )
        
        if not (is_doctor or is_patient):
            raise UnauthorizedError(
                "No tiene permisos para eliminar esta cita"
            )
            
        if is_patient:
            self._validate_patient_can_delete(appointment)
    
    def _validate_patient_can_delete(self, appointment) -> None:
        from datetime import date
        
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise BusinessRuleViolationError(
                "Solo se pueden eliminar citas programadas"
            )
            
        if appointment.date <= date.today():
            raise BusinessRuleViolationError(
                "No se pueden eliminar citas para el día de hoy o fechas pasadas"
            )
    
    def _validate_appointment_can_be_deleted(self, appointment) -> None:
        pass
            
