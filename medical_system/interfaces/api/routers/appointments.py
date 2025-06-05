from fastapi import APIRouter, HTTPException, status, Query, Response
from datetime import date, time
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

from medical_system.usecases.appointment.create_appointment import CreateAppointmentUseCase
from medical_system.usecases.appointment.cancel_appointment import CancelAppointmentUseCase
from medical_system.usecases.appointment.complete_appointment import CompleteAppointmentUseCase
from medical_system.usecases.appointment.get_doctor_appointments import GetDoctorAppointmentsUseCase
from medical_system.usecases.appointment.list_patient_appointments import ListPatientAppointmentsUseCase
from medical_system.usecases.appointment.list_all_appointments import ListAllAppointmentsUseCase
from medical_system.usecases.appointment.delete_appointment import DeleteAppointmentUseCase
from medical_system.usecases.appointment.get_available_slots import GetAvailableSlotsUseCase
from medical_system.usecases.appointment.reschedule_appointment import RescheduleAppointmentUseCase

from medical_system.usecases.dtos.appointment_dto import (
    CreateAppointmentDTO,
    AppointmentDTO,
    UpdateAppointmentDTO,
    RescheduleAppointmentDTO,
    AvailableSlotsRequestDTO,
    TimeSlotDTO
)

from medical_system.infrastructure.container import get_appointment_repository, get_patient_repository, get_doctor_repository

appointment_repo = get_appointment_repository()
patient_repo = get_patient_repository()
doctor_repo = get_doctor_repository()

router = APIRouter()

@router.get("/", response_model=List[AppointmentDTO])
async def list_appointments(
    patient_id: Optional[int] = Query(None, description="Filtrar por ID de paciente"),
    doctor_id: Optional[int] = Query(None, description="Filtrar por ID de doctor"),
    date: Optional[date] = Query(None, description="Filtrar por fecha específica (formato: YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filtrar por estado (Programada, Cancelada, Completada)")
):
    try:
        if status:
            status = status.capitalize()
            if status not in ["Programada", "Cancelada", "Completada"]:
                raise HTTPException(
                    status_code=400,
                    detail="El estado debe ser uno de: Programada, Cancelada, Completada"
                )
        
        use_case = ListAllAppointmentsUseCase(appointment_repo)
        appointments = use_case.execute(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date=date,
            status=status
        )

        return [_appointment_to_dto(appt) for appt in appointments]
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error al listar citas")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/", response_model=AppointmentDTO, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment_data: dict):
    try:
        logger.info(f"Intentando crear cita con datos: {appointment_data}")
        required_fields = ['patient_id', 'doctor_id', 'date', 'time']
        for field in required_fields:
            if field not in appointment_data:
                raise HTTPException(status_code=400, detail=f"Campo requerido faltante: {field}")

        patient = patient_repo.find_by_id(appointment_data['patient_id'])
        if not patient:
            raise HTTPException(status_code=404, detail=f"Paciente con ID {appointment_data['patient_id']} no encontrado")
        

        doctor = doctor_repo.find_by_id(appointment_data['doctor_id'])
        if not doctor:
            raise HTTPException(status_code=404, detail=f"Doctor con ID {appointment_data['doctor_id']} no encontrado")
        
        create_dto = CreateAppointmentDTO(
            patient_id=appointment_data['patient_id'],
            doctor_id=appointment_data['doctor_id'],
            date=appointment_data['date'],
            time=appointment_data['time']
        )
        
        logger.info(f"DTO creado: {create_dto}")
        
        use_case = CreateAppointmentUseCase(appointment_repo, patient_repo, doctor_repo)
        appointment = use_case.execute(create_dto)
        
        logger.info(f"Cita creada exitosamente: {appointment}")
        
        return _appointment_to_dto(appointment)
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al crear cita: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

def _appointment_to_dto(appointment):

    if not appointment:
        return None

    status_value = appointment.status.value if hasattr(appointment.status, 'value') else appointment.status
    patient_email = str(appointment.patient.email) if hasattr(appointment.patient.email, '__str__') else appointment.patient.email
    doctor_email = str(appointment.doctor.email) if hasattr(appointment.doctor.email, '__str__') else appointment.doctor.email

    from medical_system.usecases.dtos.appointment_dto import AppointmentDTO
    from medical_system.usecases.dtos.patient_dto import PatientDTO
    from medical_system.usecases.dtos.doctor_dto import DoctorDTO
    
    patient_dto = PatientDTO(
        id=appointment.patient.id,
        name=appointment.patient.name,
        email=patient_email,
        birth_date=appointment.patient.birth_date
    )
    
    doctor_dto = DoctorDTO(
        id=appointment.doctor.id,
        name=appointment.doctor.name,
        email=doctor_email,
        specialty=appointment.doctor.specialty
    )
    
    return AppointmentDTO(
        id=appointment.id,
        date=appointment.date,
        time=appointment.time,
        status=status_value,
        patient=patient_dto,
        doctor=doctor_dto,
        created_at=getattr(appointment, 'created_at', None),
        updated_at=getattr(appointment, 'updated_at', None),
        notes=getattr(appointment, 'notes', None),
        reason=getattr(appointment, 'reason', None)
    )

@router.post("/{appointment_id}/cancel", response_model=AppointmentDTO)
async def cancel_appointment(appointment_id: int, patient_id: int = Query(..., description="ID del paciente que cancela la cita")):
    use_case = CancelAppointmentUseCase(appointment_repo, patient_repo)
    try:
        appointment = use_case.execute(appointment_id, patient_id)
        return _appointment_to_dto(appointment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{appointment_id}/complete", response_model=AppointmentDTO)
async def complete_appointment(appointment_id: int, doctor_id: int = Query(..., description="ID del doctor que completa la cita")):

    use_case = CompleteAppointmentUseCase(appointment_repo)
    try:
        appointment = use_case.execute(appointment_id, doctor_id)
        return _appointment_to_dto(appointment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentDTO)
async def get_appointment(
    appointment_id: int,
    requesting_user_id: int = Query(..., description="ID del usuario que realiza la consulta")
):
    try:
        appointment = appointment_repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        if (appointment.patient.id != requesting_user_id and 
            appointment.doctor.id != requesting_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para ver esta cita"
            )
        
        return _appointment_to_dto(appointment)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al obtener cita {appointment_id}")
        raise HTTPException(status_code=500, detail="Error interno al obtener la cita")

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentDTO])
async def get_doctor_appointments(
    doctor_id: int,
    date: Optional[date] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    requesting_doctor_id: int = Query(..., description="ID del doctor que realiza la consulta")
):
    try:
        use_case = GetDoctorAppointmentsUseCase(appointment_repo, doctor_repo)
        appointments = use_case.execute(
            doctor_id=doctor_id,
            requesting_doctor_id=requesting_doctor_id,
            date=date,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        return [_appointment_to_dto(appt) for appt in appointments]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error al obtener citas del doctor")
        raise HTTPException(status_code=500, detail="Error interno al obtener las citas")

@router.get("/patient/{patient_id}", response_model=List[AppointmentDTO])
async def get_patient_appointments(
    patient_id: int,
    date: Optional[date] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    requesting_user_id: int = Query(..., description="ID del usuario que realiza la consulta")
):
    try:
        if requesting_user_id != patient_id:
            patient = patient_repo.find_by_id(patient_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Paciente no encontrado")
                
            doctor = doctor_repo.find_by_id(requesting_user_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo el paciente o su doctor pueden ver estas citas"
                )
        use_case = ListPatientAppointmentsUseCase(appointment_repo)
        appointments = use_case.execute(
            patient_id=patient_id,
            date=date,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        return [_appointment_to_dto(appt) for appt in appointments]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al obtener citas del paciente {patient_id}")
        raise HTTPException(status_code=500, detail="Error interno al obtener las citas")

@router.get("/available-slots", response_model=List[TimeSlotDTO])
async def get_available_slots(
    doctor_id: int,
    date: date,
    duration_minutes: int = 30,
    start_time: Optional[time] = None,
    end_time: Optional[time] = None
):
    try:
        request_dto = AvailableSlotsRequestDTO(
            doctor_id=doctor_id,
            date=date,
            duration_minutes=duration_minutes,
            start_time=start_time,
            end_time=end_time
        )
        
        use_case = GetAvailableSlotsUseCase(appointment_repo, doctor_repo)
        available_slots = use_case.execute(request_dto)
        return available_slots
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error al obtener horarios disponibles")
        raise HTTPException(status_code=500, detail="Error interno al obtener horarios disponibles")

@router.put("/{appointment_id}", response_model=AppointmentDTO)
async def update_appointment(
    appointment_id: int,
    update_data: Dict[str, Any],
    requesting_user_id: int = Query(..., description="ID del usuario que realiza la actualización")
):
    try:
        appointment = appointment_repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        if (appointment.patient.id != requesting_user_id and 
            appointment.doctor.id != requesting_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para actualizar esta cita"
            )
        update_dto = UpdateAppointmentDTO(
            appointment_id=appointment_id,
            **{k: v for k, v in update_data.items() if v is not None and k != 'appointment_id'}
        )
        
        for field, value in update_data.items():
            if hasattr(appointment, field) and field not in ['id', 'created_at', 'updated_at']:
                setattr(appointment, field, value)
        
        updated_appointment = appointment_repo.save(appointment)
        return _appointment_to_dto(updated_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al actualizar cita {appointment_id}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar la cita")

@router.post("/{appointment_id}/reschedule", response_model=AppointmentDTO)
async def reschedule_appointment(
    appointment_id: int,
    reschedule_data: Dict[str, Any],
    requesting_user_id: int = Query(..., description="ID del usuario que reagenda la cita")
):
    try:
        appointment = appointment_repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        if (appointment.patient.id != requesting_user_id and 
            appointment.doctor.id != requesting_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para reagendar esta cita"
            )
        
        reschedule_dto = RescheduleAppointmentDTO(
            appointment_id=appointment_id,
            new_date=reschedule_data.get('new_date'),
            new_time=reschedule_data.get('new_time'),
            reason=reschedule_data.get('reason', ''),
            requested_by=requesting_user_id
        )
        
        use_case = RescheduleAppointmentUseCase(
            appointment_repo=appointment_repo,
            patient_repo=patient_repo,
            doctor_repo=doctor_repo
        )
        
        updated_appointment = use_case.execute(reschedule_dto)
        return _appointment_to_dto(updated_appointment)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al reagendar cita {appointment_id}")
        raise HTTPException(status_code=500, detail="Error interno al reagendar la cita")

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    requesting_user_id: int = Query(..., description="ID del usuario que elimina la cita"),
    reason: Optional[str] = None
):
    try:
        appointment = appointment_repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        is_patient = appointment.patient.id == requesting_user_id
        is_doctor = appointment.doctor.id == requesting_user_id
        
        if not (is_patient or is_doctor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para eliminar esta cita"
            )
        
        use_case = DeleteAppointmentUseCase(appointment_repo)
        use_case.execute(appointment_id, requesting_user_id, reason)
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al eliminar cita {appointment_id}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar la cita")
