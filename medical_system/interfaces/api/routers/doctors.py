from fastapi import APIRouter, HTTPException, status
from typing import List
from medical_system.usecases.doctor.create_doctor import CreateDoctorUseCase
from medical_system.usecases.doctor.list_doctors_by_specialty import ListDoctorsBySpecialtyUseCase
from medical_system.usecases.doctor.update_doctor import UpdateDoctorUseCase
from medical_system.usecases.dtos.doctor_dto import CreateDoctorDTO, UpdateDoctorDTO, DoctorDTO
from medical_system.infrastructure.container import get_doctor_repository

router = APIRouter()
doctor_repo = get_doctor_repository()

def _to_dto(doctor) -> DoctorDTO:
    if not doctor:
        return None
    return DoctorDTO(
        id=doctor.id,
        name=doctor.name,
        email=str(doctor.email),
        specialty=doctor.specialty
    )

@router.post("/", response_model=DoctorDTO, status_code=status.HTTP_201_CREATED)
async def create_doctor(doctor_data: CreateDoctorDTO):
    use_case = CreateDoctorUseCase(doctor_repo)
    try:
        doctor = use_case.execute(doctor_data)
        return _to_dto(doctor)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{doctor_id}", response_model=DoctorDTO)
async def get_doctor(doctor_id: int):
    doctor = doctor_repo.find_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return _to_dto(doctor)

@router.put("/{doctor_id}", response_model=DoctorDTO)
async def update_doctor(doctor_id: int, doctor_data: UpdateDoctorDTO):
    use_case = UpdateDoctorUseCase(doctor_repo)
    try:
        doctor = use_case.execute(doctor_id, doctor_data)
        return _to_dto(doctor)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DoctorDTO])
async def list_doctors():
    doctors = doctor_repo.find_all()
    return [_to_dto(doctor) for doctor in doctors]

@router.get("/specialty/{specialty}", response_model=List[DoctorDTO])
async def list_doctors_by_specialty(specialty: str):
    use_case = ListDoctorsBySpecialtyUseCase(doctor_repo)
    doctors = use_case.execute(specialty)
    return [_to_dto(doctor) for doctor in doctors]
