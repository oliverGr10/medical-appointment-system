from typing import Dict, List, Optional

from medical_system.application.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.entities.patient import Patient
from medical_system.domain.value_objects.email import Email


class InMemoryPatientRepository(PatientRepository):
    def __init__(self):
        self._patients: Dict[int, Patient] = {}
        self._next_id = 1
        self._email_index: Dict[str, Patient] = {}

    def find_by_id(self, patient_id: int) -> Optional[Patient]:
        return self._patients.get(patient_id)

    def find_by_email(self, email: str) -> Optional[Patient]:
        return self._email_index.get(email.lower())

    def save(self, patient: Patient) -> Patient:
        if patient.id is None:
            # New patient
            patient.id = self._next_id
            self._next_id += 1
        
        # Update email index
        if hasattr(patient, 'email') and patient.email:
            self._email_index[str(patient.email).lower()] = patient
        
        # Save patient
        self._patients[patient.id] = patient
        return patient
    
    def update(self, patient: Patient) -> Patient:
        if patient.id not in self._patients:
            raise ValueError("Patient not found")
        
        # If email is being updated, update the email index
        existing = self._patients[patient.id]
        if hasattr(existing, 'email') and str(existing.email).lower() in self._email_index:
            del self._email_index[str(existing.email).lower()]
        
        if hasattr(patient, 'email') and patient.email:
            self._email_index[str(patient.email).lower()] = patient
        
        self._patients[patient.id] = patient
        return patient
    
    def find_all(self) -> List[Patient]:
        return list(self._patients.values())
