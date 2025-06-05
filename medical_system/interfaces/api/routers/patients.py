from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from medical_system.usecases.patient.create_patient import CreatePatientUseCase
from medical_system.usecases.patient.update_patient import UpdatePatientUseCase
from medical_system.usecases.dtos.patient_dto import CreatePatientDTO, UpdatePatientDTO, PatientDTO
from medical_system.infrastructure.container import get_patient_repository, get_user_repository
from medical_system.domain.entities.user import User
from ..middleware.auth_middleware import get_current_user, get_admin_user, require_roles, get_doctor_or_admin_user

router = APIRouter(
    prefix="",
    tags=["Pacientes"],
    responses={404: {"description": "No encontrado"}},
)

patient_repo = get_patient_repository()
user_repo = get_user_repository()

def _to_dto(patient) -> PatientDTO:
    if not patient:
        return None
    return PatientDTO(
        id=patient.id,
        name=patient.name,
        email=str(patient.email),
        birth_date=patient.birth_date
    )

@router.post(
    "/", 
    response_model=PatientDTO, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo paciente",
    description="Crea un nuevo registro de paciente en el sistema.",
    responses={
        201: {"description": "Paciente creado exitosamente"},
        400: {"description": "Datos inválidos"},
        403: {"description": "No autorizado"},
        409: {"description": "El paciente ya existe"}
    }
)
async def create_patient(
    patient_data: CreatePatientDTO,
    current_user: User = Depends(require_roles(["admin"]))
):

    use_case = CreatePatientUseCase(patient_repo)
    try:
        patient = use_case.execute(patient_data)
        return _to_dto(patient)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error al crear paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear el paciente"
        )

@router.get(
    "/{patient_id}", 
    response_model=PatientDTO,
    summary="Obtener información de un paciente",
    description="Obtiene la información detallada de un paciente por su ID.",
    responses={
        200: {"description": "Información del paciente obtenida exitosamente"},
        403: {"description": "No autorizado para ver este paciente"},
        404: {"description": "Paciente no encontrado"}
    }
)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(require_roles(["admin", "doctor", "patient"]))
):
    patient = patient_repo.find_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Paciente no encontrado"
        )
    
    is_admin = current_user.is_admin or current_user.has_role("admin")
    is_doctor = current_user.has_role("doctor")
    is_owner = _is_patient_owner(current_user, patient_id)
    
    if not (is_admin or is_doctor or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este paciente"
        )
    
    return _to_dto(patient)

@router.put(
    "/{patient_id}", 
    response_model=PatientDTO,
    summary="Actualizar información de un paciente",
    description="Actualiza la información de un paciente existente."
)
async def update_patient(
    patient_id: int, 
    patient_data: UpdatePatientDTO,
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin and not _is_patient_owner(current_user, patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para actualizar este recurso"
        )
        
    use_case = UpdatePatientUseCase(patient_repo)
    try:
        patient = use_case.execute(patient_id, patient_data)
        return _to_dto(patient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@router.get(
    "/", 
    response_model=List[PatientDTO],
    summary="Listar pacientes",
    description="Obtiene una lista de todos los pacientes registrados. Requiere rol de administrador o doctor.",
    responses={
        200: {"description": "Lista de pacientes obtenida exitosamente"},
        403: {"description": "No autorizado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_doctor_or_admin_user)
):

    patients = patient_repo.find_all()[skip:skip + limit]
    return [_to_dto(patient) for patient in patients]

def _is_patient_owner(current_user: User, patient_id: int) -> bool:
    patient = patient_repo.find_by_id(patient_id)
    if not patient:
        return False
        
    if hasattr(patient, 'email') and patient.email == current_user.email:
        return True

    if hasattr(current_user, 'patient_id') and current_user.patient_id == patient_id:
        return True
        
    return False
