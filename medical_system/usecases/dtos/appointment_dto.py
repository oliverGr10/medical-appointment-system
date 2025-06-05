from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional, Dict, Any
from medical_system.usecases.dtos.doctor_dto import DoctorDTO
from medical_system.usecases.dtos.patient_dto import PatientDTO

@dataclass
class CreateAppointmentDTO:
    patient_id: int
    doctor_id: int
    date: date
    time: time

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
        if isinstance(self.time, str):
            if 'T' in self.time:
                self.time = datetime.fromisoformat(self.time).time()
            else:
                self.time = datetime.strptime(self.time, "%H:%M:%S").time()


@dataclass
class GetDoctorAppointmentsDTO:
    doctor_id: int
    date: date


@dataclass
class AppointmentListDTO:
    id: int
    date: date
    time: time
    status: str
    patient_name: str
    doctor_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'time': self.time.strftime('%H:%M'),
            'status': self.status,
            'patient_name': self.patient_name,
            'doctor_name': self.doctor_name
        }

@dataclass
class AppointmentDTO(AppointmentListDTO):
    patient: Optional[PatientDTO] = None
    doctor: Optional[DoctorDTO] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    notes: Optional[str] = None
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        if self.patient:
            base_dict['patient_details'] = {
                'id': self.patient.id,
                'name': self.patient.name,
                'email': self.patient.email,
                'birth_date': self.patient.birth_date.isoformat() if self.patient.birth_date else None
            }
            
        if self.doctor:
            base_dict['doctor_details'] = {
                'id': self.doctor.id,
                'name': self.doctor.name,
                'email': self.doctor.email,
                'specialty': self.doctor.specialty
            }
        base_dict.update({
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes,
            'reason': self.reason
        })
        
        return base_dict


@dataclass
class UpdateAppointmentDTO:
    appointment_id: int
    date: Optional[date] = None
    time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):

        if all(field is None for field in [self.date, self.time, self.status, self.notes]):
            raise ValueError("Al menos un campo debe ser proporcionado para la actualización")

        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
            
        if isinstance(self.time, str):
            if 'T' in self.time:
                self.time = datetime.fromisoformat(self.time).time()
            else:
                self.time = datetime.strptime(self.time, "%H:%M:%S").time()


@dataclass
class AvailableSlotsRequestDTO:
    doctor_id: int
    date: date
    duration_minutes: int = 30
    
    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
    
    def to_dict(self) -> dict:
        return {
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat(),
            'duration_minutes': self.duration_minutes
        }


@dataclass
class RescheduleAppointmentDTO:
    appointment_id: int
    new_date: date
    new_time: time
    reason: Optional[str] = None
    requesting_user_id: Optional[int] = None
    
    def __post_init__(self):
        if isinstance(self.new_date, str):
            self.new_date = datetime.strptime(self.new_date, "%Y-%m-%d").date()
            
        if isinstance(self.new_time, str):
            if 'T' in self.new_time:
                self.new_time = datetime.fromisoformat(self.new_time).time()
            else:
                self.new_time = datetime.strptime(self.new_time, "%H:%M:%S").time()
    
    def to_dict(self) -> dict:

        return {
            'appointment_id': self.appointment_id,
            'new_date': self.new_date.isoformat(),
            'new_time': self.new_time.isoformat(),
            'reason': self.reason,
            'requesting_user_id': self.requesting_user_id
        }


@dataclass
class TimeSlotDTO:
    id: int
    start_time: time
    end_time: time
    duration_minutes: int
    is_available: bool = True
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'is_available': self.is_available
        }
