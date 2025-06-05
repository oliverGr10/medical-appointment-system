from datetime import datetime, date, time, timedelta
from typing import Optional, Dict, Any
import logging
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    BusinessRuleViolationError,
    UnauthorizedError
)

logger = logging.getLogger(__name__)

class RescheduleAppointmentUseCase:

    MIN_RESCHEDULE_NOTICE_HOURS = 24
    
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: Optional[PatientRepository] = None,
        doctor_repository: Optional[DoctorRepository] = None
    ):
        self.appointment_repo = appointment_repository
        self.patient_repo = patient_repo
        self.doctor_repo = doctor_repo
    
    def execute(self, request_dto) -> Dict[str, Any]:

        logger.info(
            f"Iniciando reagendamiento de cita {request_dto.appointment_id} "
            f"solicitado por usuario {request_dto.requested_by}"
        )

        self._validate_request(request_dto)

        appointment = self.appointment_repo.find_by_id(request_dto.appointment_id)
        if not appointment:
            raise ResourceNotFoundError("La cita especificada no existe")

        self._check_permissions(appointment, request_dto.requested_by)

        self._validate_can_reschedule(appointment)

        try:

            updated_appointment = self._create_rescheduled_appointment(
                appointment=appointment,
                new_date=request_dto.new_date,
                new_time=request_dto.new_time,
                reason=request_dto.reason
            )
            saved_appointment = self.appointment_repo.save(updated_appointment)
            
            self._log_reschedule_event(appointment, saved_appointment, request_dto.requested_by)
            
            logger.info(
                f"Cita {appointment.id} reagendada exitosamente de "
                f"{appointment.date} {appointment.time} a "
                f"{saved_appointment.date} {saved_appointment.time}"
            )
            
            return self._to_dto(saved_appointment)
            
        except Exception as e:
            logger.error(
                f"Error al reagendar cita {request_dto.appointment_id}: {str(e)}",
                exc_info=True
            )
            raise
    
    def _validate_request(self, request_dto) -> None:

        if not request_dto.appointment_id:
            raise ValidationError("Se requiere el ID de la cita")
            
        if not request_dto.new_date:
            raise ValidationError("Se requiere una nueva fecha para la cita")
            
        if not request_dto.new_time:
            raise ValidationError("Se requiere una nueva hora para la cita")
            
        if not request_dto.requested_by:
            raise ValidationError("Se requiere el ID del usuario que solicita el reagendamiento")
            
        new_datetime = datetime.combine(request_dto.new_date, request_dto.new_time)
        if new_datetime < datetime.now():
            raise ValidationError("No se puede reagendar una cita a una fecha/hora pasada")
    
    def _check_permissions(self, appointment, requesting_user_id: int) -> None:

        is_patient = hasattr(appointment, 'patient') and appointment.patient.id == requesting_user_id
        is_doctor = hasattr(appointment, 'doctor') and appointment.doctor.id == requesting_user_id

        if not (is_patient or is_doctor):
            logger.warning(
                f"Intento no autorizado de reagendar cita {appointment.id} "
                f"por usuario {requesting_user_id}"
            )
            raise UnauthorizedError(
                "No tiene permisos para reagendar esta cita"
            )
    
    def _validate_can_reschedule(self, appointment) -> None:

        if appointment.status != AppointmentStatus.SCHEDULED:
            raise BusinessRuleViolationError(
                f"No se puede reagendar una cita en estado '{appointment.status.name.lower()}'"
            )

        appointment_datetime = datetime.combine(appointment.date, appointment.time)
        min_notice = timedelta(hours=self.MIN_RESCHEDULE_NOTICE_HOURS)
        
        if datetime.now() + min_notice > appointment_datetime:
            raise BusinessRuleViolationError(
                f"No se puede reagendar con menos de {self.MIN_RESCHEDULE_NOTICE_HOURS} "
                "horas de anticipación"
            )
    
    def _create_rescheduled_appointment(
        self,
        appointment: Appointment,
        new_date: date,
        new_time: time,
        reason: Optional[str] = None
    ) -> Appointment:
        updated_appointment = Appointment(
            id=appointment.id,
            patient=appointment.patient,
            doctor=appointment.doctor,
            date=new_date,
            time=new_time,
            status=appointment.status,
            reason=reason or appointment.reason,
            created_at=appointment.created_at,
            updated_at=datetime.now()
        )
        
        if hasattr(appointment, 'notes'):
            updated_appointment.notes = appointment.notes
            
        if hasattr(appointment, 'cancellation_reason'):
            updated_appointment.cancellation_reason = appointment.cancellation_reason
        
        return updated_appointment
    
    def _log_reschedule_event(
        self, 
        original_appointment: Appointment, 
        updated_appointment: Appointment,
        requested_by: int
    ) -> None:

        log_message = (
            f"Cita {original_appointment.id} reagendada por usuario {requested_by}. "
            f"Antes: {original_appointment.date} {original_appointment.time}. "
            f"Después: {updated_appointment.date} {updated_appointment.time}."
        )
        logger.info(log_message)

    @staticmethod
    def _to_dto(appointment) -> Dict[str, Any]:
        return {
            'id': appointment.id,
            'date': appointment.date,
            'time': appointment.time,
            'status': appointment.status.name.lower(),
            'patient': {
                'id': appointment.patient.id,
                'name': appointment.patient.name,
                'email': str(appointment.patient.email),
            },
            'doctor': {
                'id': appointment.doctor.id,
                'name': appointment.doctor.name,
                'email': str(appointment.doctor.email),
                'specialty': appointment.doctor.specialty,
            },
            'created_at': appointment.created_at,
            'updated_at': appointment.updated_at,
            'reason': getattr(appointment, 'reason', None),
        }
