from datetime import time, date, datetime, timedelta
from typing import List
import logging
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    BusinessRuleViolationError
)
from medical_system.usecases.dtos.appointment_dto import TimeSlotDTO

logger = logging.getLogger(__name__)

class GetAvailableSlotsUseCase:

    DEFAULT_WORK_HOURS = {
        'start': time(9, 0),
        'end': time(18, 0),
        'lunch_start': time(13, 0),
        'lunch_end': time(14, 0),
    }

    WORK_DAYS = [0, 1, 2, 3, 4]
    
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        doctor_repository: DoctorRepository
    ):
        self.appointment_repo = appointment_repository
        self.doctor_repo = doctor_repository
    
    def execute(self, request_dto) -> List[TimeSlotDTO]:

        logger.info(
            f"Buscando horarios disponibles para doctor {request_dto.doctor_id} "
            f"el {request_dto.date}"
        )
        
        self._validate_request(request_dto)
        
        doctor = self.doctor_repo.find_by_id(request_dto.doctor_id)
        if not doctor:
            raise ResourceNotFoundError("El doctor especificado no existe")

        work_schedule = self._get_doctor_schedule(doctor, request_dto.date)
        
        existing_appointments = self.appointment_repo.find_by_doctor_and_date(
            doctor_id=request_dto.doctor_id,
            date=request_dto.date,
            status='scheduled'
        )
        
        available_slots = self._calculate_available_slots(
            work_schedule=work_schedule,
            existing_appointments=existing_appointments,
            duration_minutes=request_dto.duration_minutes
        )
        
        logger.info(f"Encontrados {len(available_slots)} horarios disponibles")
        return available_slots
    
    def _validate_request(self, request_dto) -> None:

        if not request_dto.doctor_id:
            raise ValidationError("Se requiere el ID del doctor")
            
        if not request_dto.date:
            raise ValidationError("Se requiere una fecha para buscar horarios")
            
        if request_dto.date < date.today():
            raise ValidationError("No se pueden buscar horarios en fechas pasadas")
            
        if request_dto.duration_minutes <= 0:
            raise ValidationError("La duración debe ser mayor a 0 minutos")
            
        if request_dto.date.weekday() not in self.WORK_DAYS:
            raise BusinessRuleViolationError(
                "No hay disponibilidad los fines de semana"
            )
    
    def _get_doctor_schedule(
        self, 
        doctor, 
        schedule_date: date
    ) -> dict:

        schedule = {
            'start': self.DEFAULT_WORK_HOURS['start'],
            'end': self.DEFAULT_WORK_HOURS['end'],
            'lunch_start': self.DEFAULT_WORK_HOURS['lunch_start'],
            'lunch_end': self.DEFAULT_WORK_HOURS['lunch_end'],
            'unavailable_periods': []
        }

        if schedule_date.weekday() == 4:
            schedule['end'] = time(14, 0)
            schedule['lunch_start'] = time(12, 30)
            schedule['lunch_end'] = time(13, 30)
        
        return schedule
    
    def _calculate_available_slots(
        self,
        work_schedule: dict,
        existing_appointments: list,
        duration_minutes: int
    ) -> List[TimeSlotDTO]:

        date_ref = datetime.now().date()
        busy_blocks = []
        lunch_start = datetime.combine(date_ref, work_schedule['lunch_start'])
        lunch_end = datetime.combine(date_ref, work_schedule['lunch_end'])
        busy_blocks.append((lunch_start, lunch_end))

        for appt in existing_appointments:
            appt_start = datetime.combine(date_ref, appt.time)
            appt_end = appt_start + timedelta(minutes=appt.duration_minutes or 30)
            busy_blocks.append((appt_start, appt_end))
        
        busy_blocks.sort()
        available_slots = []
        current_time = datetime.combine(date_ref, work_schedule['start'])
        end_time = datetime.combine(date_ref, work_schedule['end'])
        
        slot_index = 1
        
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)

            if slot_end > end_time:
                break
            
            is_available = True
            for busy_start, busy_end in busy_blocks:
                if (current_time < busy_end and slot_end > busy_start):
                    is_available = False
                    current_time = busy_end
                    break
            
            if is_available:
                available_slots.append(
                    TimeSlotDTO(
                        id=slot_index,
                        start_time=current_time.time(),
                        end_time=slot_end.time(),
                        duration_minutes=duration_minutes
                    )
                )
                slot_index += 1
                current_time = slot_end

        return available_slots
