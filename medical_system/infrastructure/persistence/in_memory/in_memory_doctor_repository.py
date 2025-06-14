from typing import Dict, List, Optional
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.entities.doctor import Doctor

class InMemoryDoctorRepository(DoctorRepository):
    def __init__(self):
        self._doctors: Dict[int, Doctor] = {}
        self._next_id = 1
        self._email_index: Dict[str, Doctor] = {}
        self._specialty_index: Dict[str, List[Doctor]] = {}

    def find_by_id(self, doctor_id: int) -> Optional[Doctor]:
        return self._doctors.get(doctor_id)

    def find_by_email(self, email: str) -> Optional[Doctor]:
        return self._email_index.get(email.lower())

    def find_by_specialty(self, specialty: str) -> List[Doctor]:
        return self._specialty_index.get(specialty.lower().strip(), []).copy()

    def save(self, doctor: Doctor) -> Doctor:
        if doctor.id is None:
            doctor.id = self._next_id
            self._next_id += 1
        
        self._update_indexes(doctor)
        return doctor
    
    def update(self, doctor: Doctor) -> Doctor:
        if doctor.id not in self._doctors:
            raise ValueError("Doctor not found")

        existing = self._doctors[doctor.id]
        self._remove_from_indexes(existing)
        self._update_indexes(doctor)
        self._doctors[doctor.id] = doctor
        return doctor
    
    def find_all(self) -> List[Doctor]:
        return list(self._doctors.values())
    
    def _update_indexes(self, doctor: Doctor):
        self._doctors[doctor.id] = doctor

        if hasattr(doctor, 'email') and doctor.email:
            self._email_index[str(doctor.email).lower()] = doctor

        if hasattr(doctor, 'specialty') and doctor.specialty:
            specialty_key = doctor.specialty.lower().strip()
            if specialty_key not in self._specialty_index:
                self._specialty_index[specialty_key] = []
            if doctor not in self._specialty_index[specialty_key]:
                self._specialty_index[specialty_key].append(doctor)
    
    def _remove_from_indexes(self, doctor: Doctor):
        
        if hasattr(doctor, 'email') and doctor.email and str(doctor.email).lower() in self._email_index:
            del self._email_index[str(doctor.email).lower()]

        if hasattr(doctor, 'specialty') and doctor.specialty:
            specialty_key = doctor.specialty.lower().strip()
            if specialty_key in self._specialty_index:
                if doctor in self._specialty_index[specialty_key]:
                    self._specialty_index[specialty_key].remove(doctor)
