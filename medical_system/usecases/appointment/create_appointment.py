from datetime import datetime
from medical_system.usecases.dtos.appointment_dto import CreateAppointmentDTO, AppointmentDTO
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.entities.appointment import Appointment
from medical_system.domain.value_objects.reservation_status import AppointmentStatus


class CreateAppointmentUseCase:

    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: PatientRepository,
        doctor_repository: DoctorRepository,
    ):
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository

    def execute(self, appointment_dto: CreateAppointmentDTO) -> AppointmentDTO:

        patient = self.patient_repository.find_by_id(appointment_dto.patient_id)
        if not patient:
            raise ValueError(f"No se encontró el paciente con ID: {appointment_dto.patient_id}")

        doctor = self.doctor_repository.find_by_id(appointment_dto.doctor_id)
        if not doctor:
            raise ValueError(f"No se encontró el doctor con ID: {appointment_dto.doctor_id}")

        existing_appointment = self.appointment_repository.find_by_doctor_patient_datetime(
            doctor_id=doctor.id,
            patient_id=patient.id,
            date=appointment_dto.date,
            time=appointment_dto.time
        )
        if existing_appointment:
            raise ValueError("Ya existe una cita idéntica")

        same_time_appointments = self.appointment_repository.find_patient_appointments_at_same_time(
            patient_id=patient.id,
            date=appointment_dto.date,
            time=appointment_dto.time
        )
        if same_time_appointments:
            raise ValueError("Ya tienes una cita programada a esta misma hora")

        try:
            same_day_appointments = self.appointment_repository.find_by_patient_and_date(
                patient_id=patient.id,
                date=appointment_dto.date
            )
            if same_day_appointments:
                raise ValueError("Solo puedes tener una cita por día")
        except Exception as e:
            raise

        try:
            appointments = self.appointment_repository.find_by_doctor_and_date(
                doctor_id=doctor.id, date=appointment_dto.date
            )
            requested_datetime = datetime.combine(appointment_dto.date, appointment_dto.time)

            for appointment in appointments:
                appointment_datetime = datetime.combine(appointment.date, appointment.time)
                time_diff = abs((appointment_datetime - requested_datetime).total_seconds())

                if time_diff < 1800:  # 30 minutos
                    raise ValueError("El doctor no está disponible en el horario solicitado (debe haber al menos 30 minutos entre citas)")
        except Exception as e:
            raise

        try:
            appointment = Appointment(
                date=appointment_dto.date,
                time=appointment_dto.time,
                status=AppointmentStatus.SCHEDULED,
                patient=patient,
                doctor=doctor,
            )
            saved_appointment = self.appointment_repository.save(appointment)
            return self._to_dto(saved_appointment)
        except Exception as e:
            raise
    
    @staticmethod
    def _to_dto(appointment: Appointment) -> AppointmentDTO:
        from medical_system.usecases.dtos.patient_dto import PatientDTO
        from medical_system.usecases.dtos.doctor_dto import DoctorDTO
        
        # Obtener los nombres del paciente y el doctor
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