from typing import List
from medical_system.usecases.dtos.doctor_dto import DoctorDTO
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository

class ListDoctorsBySpecialtyUseCase:
    def __init__(self, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    def execute(self, specialty: str) -> List[DoctorDTO]:
        doctors = self.doctor_repository.find_by_specialty(specialty)

        return [self._to_dto(doctor) for doctor in doctors]
    
    @staticmethod
    def _to_dto(doctor) -> DoctorDTO:
        return DoctorDTO(
            id=doctor.id,
            name=doctor.name,
            email=str(doctor.email),
            specialty=doctor.specialty,
        )
