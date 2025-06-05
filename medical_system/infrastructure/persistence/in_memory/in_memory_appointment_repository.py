from datetime import date, datetime, time
from typing import Dict, List, Optional
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.entities.appointment import Appointment


class InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self):
        self._appointments: Dict[int, Appointment] = {}
        self._next_id = 1
        self._doctor_date_index: Dict[tuple[int, date], List[Appointment]] = {}
        self._patient_index: Dict[int, List[Appointment]] = {}

    def find_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self._appointments.get(appointment_id)

    def save(self, appointment: Appointment) -> Appointment:
        if appointment.id is None:
            appointment.id = self._next_id
            self._next_id += 1
        
        self._update_indexes(appointment)
        self._appointments[appointment.id] = appointment
        return appointment
    
    def update(self, appointment: Appointment) -> Appointment:
        if appointment.id not in self._appointments:
            raise ValueError("Appointment not found")
        existing = self._appointments[appointment.id]
        self._remove_from_indexes(existing)
        self._update_indexes(appointment)
        self._appointments[appointment.id] = appointment
        return appointment
    
    def find_by_doctor_and_date(self, doctor_id: int, date: date) -> List[Appointment]:
        return self._doctor_date_index.get((doctor_id, date), []).copy()
    
    def find_by_patient(self, patient_id: int) -> List[Appointment]:
        return self._patient_index.get(patient_id, []).copy()
    
    def find_by_patient_and_date(self, patient_id: int, date: date) -> List[Appointment]:
        patient_appointments = self.find_by_patient(patient_id)
        return [apt for apt in patient_appointments if apt.date == date]
    
    def find_by_doctor_patient_datetime(
        self, doctor_id: int, patient_id: int, date: date, time: time
    ) -> Optional[Appointment]:
        appointments = self.find_by_doctor_and_date(doctor_id, date)
        for apt in appointments:
            if apt.patient.id == patient_id and apt.time == time:
                return apt
        return None
    
    def find_patient_appointments_at_same_time(
        self, patient_id: int, date: date, time: time
    ) -> List[Appointment]:
        patient_appointments = self.find_by_patient(patient_id)
        return [
            apt for apt in patient_appointments 
            if apt.date == date and apt.time == time
        ]
    
    def find_available_slots(self, doctor_id: int, date: date) -> List[datetime]:
        appointments = self.find_by_doctor_and_date(doctor_id, date)
        booked_times = {apt.time for apt in appointments}
        
        all_slots = [
            time(hour=h, minute=m)
            for h in range(8, 20)
            for m in [0, 30]
        ]
        
        # Filter out booked times
        available = [
            datetime.combine(date, t)
            for t in all_slots
            if t not in booked_times
        ]
        
        return available
    
    def find_all(self) -> List[Appointment]:
        return list(self._appointments.values())
    
    def delete(self, appointment_id: int) -> None:
        if appointment_id in self._appointments:
            appointment = self._appointments[appointment_id]
            self._remove_from_indexes(appointment)
            del self._appointments[appointment_id]
    
    def _update_indexes(self, appointment: Appointment):
        key = (appointment.doctor.id, appointment.date)
        if key not in self._doctor_date_index:
            self._doctor_date_index[key] = []
        if appointment not in self._doctor_date_index[key]:
            self._doctor_date_index[key].append(appointment)
        
        if appointment.patient.id not in self._patient_index:
            self._patient_index[appointment.patient.id] = []
        if appointment not in self._patient_index[appointment.patient.id]:
            self._patient_index[appointment.patient.id].append(appointment)
    
    def _remove_from_indexes(self, appointment: Appointment):
        key = (appointment.doctor.id, appointment.date)
        if key in self._doctor_date_index and appointment in self._doctor_date_index[key]:
            self._doctor_date_index[key].remove(appointment)
        if appointment.patient.id in self._patient_index:
            if appointment in self._patient_index[appointment.patient.id]:
                self._patient_index[appointment.patient.id].remove(appointment)
