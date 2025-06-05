from medical_system.usecases.dtos.patient_dto import UpdatePatientDTO, PatientDTO
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class UpdatePatientUseCase:
    def __init__(self, patient_repository: PatientRepository):
        self.patient_repository = patient_repository

    def execute(self, patient_dto: UpdatePatientDTO, is_admin: bool = False) -> PatientDTO:

        if not is_admin:
            raise UnauthorizedError("Only administrators can update patient information")

        patient = self.patient_repository.find_by_id(patient_dto.id)
        if not patient:
            raise ValueError("Patient not found")
        
        if patient_dto.email and patient_dto.email != str(patient.email):
            existing_patient = self.patient_repository.find_by_email(patient_dto.email)
            if existing_patient and existing_patient.id != patient.id:
                raise ValueError("Email is already in use by another patient")

        if patient_dto.name:
            patient.name = patient_dto.name
        if patient_dto.email:
            patient.email = Email(patient_dto.email)
        if patient_dto.birth_date:
            patient.birth_date = patient_dto.birth_date

        updated_patient = self.patient_repository.update(patient)
        result = PatientDTO(
            id=updated_patient.id,
            name=updated_patient.name,
            email=str(updated_patient.email),
            birth_date=updated_patient.birth_date,
        )
        return result
