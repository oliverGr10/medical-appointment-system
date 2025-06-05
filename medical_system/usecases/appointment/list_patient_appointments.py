from datetime import date
from typing import List, Optional, Dict, Any
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.entities.appointment import AppointmentStatus


class ListPatientAppointmentsUseCase:

    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: Optional[PatientRepository] = None,
    ):
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository

    def execute(
        self,
        patient_id: int,
        date: Optional[date] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        requesting_user_id: Optional[int] = None,
        **filters
    ) -> List[Dict[str, Any]]:

        if requesting_user_id is not None and requesting_user_id != patient_id:

            pass

        self._validate_parameters(date, status, start_date, end_date)

        filters['patient_id'] = patient_id
        if date:
            filters['date'] = date
        if status:
            try:
                filters['status'] = AppointmentStatus[status.upper()]
            except KeyError:
                raise ValueError(f"Estado no válido: {status}")
 
        appointments = self.appointment_repository.find_by_patient(
            patient_id=patient_id,
            **filters
        )

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
    
    @staticmethod
    def _to_dto(appointment) -> Dict[str, Any]:
        return ListPatientAppointmentsUseCase._to_dict(appointment)
    
    @staticmethod
    def _to_dict(appointment) -> Dict[str, Any]:
        return {
            'id': appointment.id,
            'date': appointment.date,
            'time': appointment.time,
            'status': appointment.status.name.lower(),
            'patient': {
                'id': appointment.patient.id,
                'name': appointment.patient.name,
                'email': str(appointment.patient.email),
                'birth_date': appointment.patient.birth_date,
            },
            'doctor': {
                'id': appointment.doctor.id,
                'name': appointment.doctor.name,
                'email': str(appointment.doctor.email),
                'specialty': appointment.doctor.specialty,
            },
            'created_at': appointment.created_at,
            'updated_at': appointment.updated_at,
            'notes': getattr(appointment, 'notes', None),
            'reason': getattr(appointment, 'reason', None)
        }
