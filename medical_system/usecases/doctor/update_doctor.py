from medical_system.usecases.dtos.doctor_dto import UpdateDoctorDTO, DoctorDTO
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class UpdateDoctorUseCase:
    def __init__(self, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    def execute(self, doctor_id: int, doctor_dto: UpdateDoctorDTO, is_admin: bool = False) -> DoctorDTO:
        if not is_admin:
            raise UnauthorizedError("Only administrators can update doctor information")

        doctor = self.doctor_repository.find_by_id(doctor_id)
        
        if not doctor:
            raise ValueError("Doctor not found")
        
        if doctor_dto.email and doctor_dto.email != str(doctor.email):
            existing_doctor = self.doctor_repository.find_by_email(doctor_dto.email)
            if existing_doctor and existing_doctor.id != doctor.id:
                raise ValueError("Email is already in use by another doctor")

        if doctor_dto.name:
            doctor.name = doctor_dto.name
        if doctor_dto.email:
            doctor.email = Email(doctor_dto.email)
        if doctor_dto.specialty:
            doctor.specialty = doctor_dto.specialty

        updated_doctor = self.doctor_repository.update(doctor)

        return DoctorDTO(
            id=updated_doctor.id,
            name=updated_doctor.name,
            email=str(updated_doctor.email),
            specialty=updated_doctor.specialty,
        )
