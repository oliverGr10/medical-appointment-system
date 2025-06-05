from fastapi import APIRouter, HTTPException, status
from typing import List
from medical_system.usecases.patient.create_patient import CreatePatientUseCase
from medical_system.usecases.patient.update_patient import UpdatePatientUseCase
from medical_system.usecases.dtos.patient_dto import CreatePatientDTO, UpdatePatientDTO, PatientDTO
from medical_system.infrastructure.container import get_patient_repository

router = APIRouter()
patient_repo = get_patient_repository()

def _to_dto(patient) -> PatientDTO:
    if not patient:
        return None
    return PatientDTO(
        id=patient.id,
        name=patient.name,
        email=str(patient.email),
        birth_date=patient.birth_date
    )

@router.post("/", response_model=PatientDTO, status_code=status.HTTP_201_CREATED)
async def create_patient(patient_data: CreatePatientDTO):
    use_case = CreatePatientUseCase(patient_repo)
    try:
        patient = use_case.execute(patient_data)
        return _to_dto(patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{patient_id}", response_model=PatientDTO)
async def get_patient(patient_id: int):
    patient = patient_repo.find_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return _to_dto(patient)

@router.put("/{patient_id}", response_model=PatientDTO)
async def update_patient(patient_id: int, patient_data: UpdatePatientDTO):
    use_case = UpdatePatientUseCase(patient_repo)
    try:
        patient = use_case.execute(patient_id, patient_data)
        return _to_dto(patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[PatientDTO])
async def list_patients():
    patients = patient_repo.find_all()
    return [_to_dto(patient) for patient in patients]
