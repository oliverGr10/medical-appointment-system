from datetime import date
from typing import List, Optional, Dict, Any
from medical_system.domain.entities.appointment import AppointmentStatus
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository

class ListAllAppointmentsUseCase:

    def __init__(
        self, 
        appointment_repository: AppointmentRepository,
        patient_repository: Optional[PatientRepository] = None,
        doctor_repository: Optional[DoctorRepository] = None
    ):
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository

    def execute(
        self,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        date: Optional[date] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters
    ) -> List[Dict[str, Any]]:
        self._validate_parameters(date, status, start_date, end_date)
        
        appointments = self.appointment_repository.find_all()
        
        if patient_id is not None:
            appointments = [apt for apt in appointments if apt.patient.id == patient_id]
            
        if doctor_id is not None:
            appointments = [apt for apt in appointments if apt.doctor.id == doctor_id]
            
        if date is not None:
            appointments = [apt for apt in appointments if apt.date == date]
            
        if status is not None:
            try:
                status_enum = AppointmentStatus[status.upper()]
                appointments = [apt for apt in appointments if apt.status == status_enum]
            except KeyError:
                raise ValueError(f"Estado no válido: {status}")
        
        if start_date or end_date:
            appointments = self._filter_by_date_range(appointments, start_date, end_date)
        
        appointments.sort(key=lambda x: (x.date, x.time), reverse=True)
        
        return [self._to_dict(apt) for apt in appointments]
    
    def _validate_parameters(
        self,
        date: Optional[date],
        status: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> None:

        if date and (start_date or end_date):
            raise ValueError(
                "No se puede especificar una fecha específica y un rango de fechas simultáneamente"
            )
        
        if (start_date and not end_date) or (not start_date and end_date):
            raise ValueError(
                "Se deben especificar tanto la fecha de inicio como la de fin para el rango"
            )
        
        if start_date and end_date and start_date > end_date:
            raise ValueError(
                "La fecha de inicio no puede ser posterior a la fecha de fin"
            )
        
        if status:
            valid_statuses = [s.name.lower() for s in AppointmentStatus]
            if status.lower() not in valid_statuses:
                raise ValueError(
                    f"Estado no válido. Debe ser uno de: {', '.join(valid_statuses)}"
                )
    
    def _filter_by_date_range(
        self,
        appointments: list,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> list:
        if not start_date or not end_date:
            return appointments
            
        return [
            apt for apt in appointments
            if start_date <= apt.date <= end_date
        ]
    
    def _to_dict(self, appointment):
        appointment_dict = {
            'id': appointment.id,
            'date': appointment.date.isoformat(),
            'time': appointment.time.isoformat(),
            'status': appointment.status.value,
            'patient': {
                'id': appointment.patient.id,
                'name': appointment.patient.name,
                'email': str(appointment.patient.email),
                'birth_date': getattr(appointment.patient, 'birth_date', None),
            },
            'doctor': {
                'id': appointment.doctor.id,
                'name': appointment.doctor.name,
                'email': str(appointment.doctor.email),
                'specialty': getattr(appointment.doctor, 'specialty', None),
            },
            'notes': getattr(appointment, 'notes', None),
            'reason': getattr(appointment, 'reason', None),
            'cancellation_reason': getattr(appointment, 'cancellation_reason', None)
        }
        
        if hasattr(appointment, 'created_at'):
            appointment_dict['created_at'] = appointment.created_at.isoformat() if appointment.created_at else None
        if hasattr(appointment, 'updated_at'):
            appointment_dict['updated_at'] = appointment.updated_at.isoformat() if hasattr(appointment, 'updated_at') and appointment.updated_at else None
            
        return appointment_dict
