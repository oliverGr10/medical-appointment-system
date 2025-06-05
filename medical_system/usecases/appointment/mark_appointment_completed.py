from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.usecases.dtos.appointment_dto import AppointmentDTO
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.value_objects.reservation_status import AppointmentStatus

class MarkAppointmentCompletedUseCase:

    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    def execute(self, appointment_id: int, doctor_id: int) -> AppointmentDTO:

        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Cita no encontrada")
            
        if appointment.doctor.id != doctor_id:
            raise UnauthorizedError("No estás autorizado para marcar esta cita como completada")
            
        appointment.status = AppointmentStatus.COMPLETED
        
        updated_appointment = self.appointment_repository.save(appointment)
        
        return self._to_dto(updated_appointment)
    
    @staticmethod
    def _to_dto(appointment) -> AppointmentDTO:

        from medical_system.usecases.dtos.patient_dto import PatientDTO
        from medical_system.usecases.dtos.doctor_dto import DoctorDTO
        
        patient_name = appointment.patient.name
        doctor_name = appointment.doctor.name
        
        return AppointmentDTO(
            id=appointment.id,
            date=appointment.date,
            time=appointment.time,
            status=str(appointment.status).lower(),
            patient_name=patient_name,
            doctor_name=doctor_name,
            patient=PatientDTO(
                id=appointment.patient.id,
                name=patient_name,
                email=str(appointment.patient.email),
                birth_date=appointment.patient.birth_date,
            ),
            doctor=DoctorDTO(
                id=appointment.doctor.id,
                name=doctor_name,
                email=str(appointment.doctor.email),
                specialty=appointment.doctor.specialty,
            ),
        )
