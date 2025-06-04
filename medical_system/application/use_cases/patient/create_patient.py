from datetime import date
from typing import Optional

from medical_system.application.dtos.patient_dto import CreatePatientDTO, PatientDTO
from medical_system.application.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.entities.patient import Patient
from medical_system.domain.value_objects.email import Email


class CreatePatientUseCase:
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository

    def execute(self, patient_dto: CreatePatientDTO) -> PatientDTO:
        # Check if patient with this email already exists
        existing_patient = self.patient_repository.find_by_email(patient_dto.email)
        if existing_patient:
            raise ValueError("A patient with this email already exists")

        # Create the patient entity
        patient = Patient(
            name=patient_dto.name,
            email=Email(patient_dto.email),
            birth_date=patient_dto.birth_date,
        )

        # Save the patient
        saved_patient = self.patient_repository.save(patient)

        # Return the DTO
        return self._to_dto(saved_patient)

    
    @staticmethod
    def _to_dto(patient: Patient) -> PatientDTO:
        return PatientDTO(
            id=patient.id,
            name=patient.name,
            email=str(patient.email),
            birth_date=patient.birth_date,
        )
