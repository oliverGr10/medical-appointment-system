from medical_system.usecases.dtos.doctor_dto import CreateDoctorDTO, DoctorDTO
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email

class CreateDoctorUseCase:
    def __init__(self, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    def execute(self, doctor_dto: CreateDoctorDTO) -> DoctorDTO:
        existing_doctor = self.doctor_repository.find_by_email(doctor_dto.email)
        if existing_doctor:
            raise ValueError("A doctor with this email already exists")

        doctor = Doctor(
            name=doctor_dto.name,
            email=Email(doctor_dto.email),
            specialty=doctor_dto.specialty,
        )

        saved_doctor = self.doctor_repository.save(doctor)

        return self._to_dto(saved_doctor)
    
    @staticmethod
    def _to_dto(doctor: Doctor) -> DoctorDTO:
        return DoctorDTO(
            id=doctor.id,
            name=doctor.name,
            email=str(doctor.email),
            specialty=doctor.specialty,
        )
