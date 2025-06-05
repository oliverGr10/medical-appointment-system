from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from medical_system.usecases.doctor.create_doctor import CreateDoctorUseCase
from medical_system.usecases.doctor.list_doctors_by_specialty import ListDoctorsBySpecialtyUseCase
from medical_system.usecases.doctor.update_doctor import UpdateDoctorUseCase
from medical_system.usecases.dtos.doctor_dto import CreateDoctorDTO, UpdateDoctorDTO, DoctorDTO
from medical_system.infrastructure.container import get_doctor_repository
from medical_system.domain.entities.user import User
from ..middleware.auth_middleware import require_roles, get_admin_user

router = APIRouter(
    prefix="",
    tags=["Doctores"],
    responses={404: {"description": "No encontrado"}},
)
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

@router.post(
    "/", 
    response_model=DoctorDTO, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo doctor",
    description="Crea un nuevo registro de doctor en el sistema. Requiere rol de administrador.",
    responses={
        201: {"description": "Doctor creado exitosamente"},
        400: {"description": "Datos inválidos"},
        403: {"description": "No autorizado"},
        409: {"description": "El doctor ya existe"}
    }
)
async def create_doctor(
    doctor_data: CreateDoctorDTO,
    current_user: User = Depends(get_admin_user)
):

    use_case = CreateDoctorUseCase(doctor_repo)
    try:
        doctor = use_case.execute(doctor_data)
        return _to_dto(doctor)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear el doctor"
        )

@router.get(
    "/{doctor_id}", 
    response_model=DoctorDTO,
    summary="Obtener información de un doctor",
    description="Obtiene la información detallada de un doctor por su ID. Público.",
    responses={
        200: {"description": "Información del doctor obtenida exitosamente"},
        404: {"description": "Doctor no encontrado"}
    }
)
async def get_doctor(doctor_id: int):

    doctor = doctor_repo.find_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Doctor no encontrado"
        )
    return _to_dto(doctor)

@router.put(
    "/{doctor_id}", 
    response_model=DoctorDTO,
    summary="Actualizar información de un doctor",
    description="Actualiza la información de un doctor existente. Requiere rol de administrador o ser el mismo doctor.",
    responses={
        200: {"description": "Doctor actualizado exitosamente"},
        400: {"description": "Datos inválidos"},
        403: {"description": "No autorizado"},
        404: {"description": "Doctor no encontrado"}
    }
)
async def update_doctor(
    doctor_id: int, 
    doctor_data: UpdateDoctorDTO,
    current_user: User = Depends(require_roles(["admin", "doctor"]))
):

    doctor = doctor_repo.find_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor no encontrado"
        )

    is_admin = current_user.is_admin or current_user.has_role("admin")
    is_self = str(doctor.email).lower() == current_user.email.lower()
    
    if not (is_admin or is_self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede actualizar su propia información"
        )
    
    use_case = UpdateDoctorUseCase(doctor_repo)
    try:
        doctor = use_case.execute(doctor_id, doctor_data)
        return _to_dto(doctor)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar el doctor"
        )

@router.get(
    "/", 
    response_model=List[DoctorDTO],
    summary="Listar doctores",
    description="Obtiene una lista de todos los doctores registrados. Público.",
    responses={
        200: {"description": "Lista de doctores obtenida exitosamente"},
        500: {"description": "Error interno del servidor"}
    }
)
async def list_doctors(
    specialty: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):

    try:
        if specialty:
            use_case = ListDoctorsBySpecialtyUseCase(doctor_repo)
            doctors = use_case.execute(specialty)
        else:
            doctors = doctor_repo.find_all()
            
        return [_to_dto(doctor) for doctor in doctors[skip:skip + limit]]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de doctores"
        )

@router.get("/specialty/{specialty}", response_model=List[DoctorDTO])
async def list_doctors_by_specialty(specialty: str):
    use_case = ListDoctorsBySpecialtyUseCase(doctor_repo)
    doctors = use_case.execute(specialty)
    return [_to_dto(doctor) for doctor in doctors]
