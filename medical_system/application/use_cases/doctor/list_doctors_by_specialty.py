from typing import List

from medical_system.application.dtos.doctor_dto import DoctorDTO
from medical_system.application.ports.repositories.doctor_repository import DoctorRepository


class ListDoctorsBySpecialtyUseCase:
    def __init__(self, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    def execute(self, specialty: str) -> List[DoctorDTO]:
        # Get doctors by specialty (case-insensitive search)
        doctors = self.doctor_repository.find_by_specialty(specialty)
        
        # Convert to DTOs
        return [self._to_dto(doctor) for doctor in doctors]
    
    @staticmethod
    def _to_dto(doctor) -> DoctorDTO:
        return DoctorDTO(
            id=doctor.id,
            name=doctor.name,
            email=str(doctor.email),
            specialty=doctor.specialty,
        )
