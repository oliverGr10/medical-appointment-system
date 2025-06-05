from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import date
from medical_system.usecases.appointment.list_all_appointments import ListAllAppointmentsUseCase
from medical_system.usecases.dtos.appointment_dto import AppointmentDTO
from medical_system.infrastructure.persistence.in_memory.in_memory_appointment_repository import InMemoryAppointmentRepository

router = APIRouter()
appointment_repo = InMemoryAppointmentRepository()

@router.get("/appointments", response_model=List[AppointmentDTO])
async def list_all_appointments(
    status: Optional[str] = Query(None, description="Filtrar por estado (scheduled, cancelled, completed)"),
    start_date: Optional[date] = Query(None, description="Fecha de inicio para filtrar citas"),
    end_date: Optional[date] = Query(None, description="Fecha de fin para filtrar citas")
):

    use_case = ListAllAppointmentsUseCase(appointment_repo)
    appointments = use_case.execute()
    
    if status:
        appointments = [a for a in appointments if a.status == status]
    if start_date:
        appointments = [a for a in appointments if a.date >= start_date]
    if end_date:
        appointments = [a for a in appointments if a.date <= end_date]
    
    return appointments
