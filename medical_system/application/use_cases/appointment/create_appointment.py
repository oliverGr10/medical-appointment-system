from datetime import datetime
from medical_system.application.dtos.appointment_dto import CreateAppointmentDTO, AppointmentDTO
from medical_system.application.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.application.ports.repositories.doctor_repository import DoctorRepository
from medical_system.application.ports.repositories.patient_repository import PatientRepository
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
        # Get patient and doctor
        patient = self.patient_repository.find_by_id(appointment_dto.patient_id)
        if not patient:
            raise ValueError("Patient not found")

        doctor = self.doctor_repository.find_by_id(appointment_dto.doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        # Check for duplicate appointment
        existing_appointment = self.appointment_repository.find_by_doctor_patient_datetime(
            doctor_id=doctor.id,
            patient_id=patient.id,
            date=appointment_dto.date,
            time=appointment_dto.time
        )
        if existing_appointment:
            raise ValueError("This appointment already exists")

        # Check if patient already has an appointment at the same time
        same_time_appointments = self.appointment_repository.find_patient_appointments_at_same_time(
            patient_id=patient.id,
            date=appointment_dto.date,
            time=appointment_dto.time
        )
        if same_time_appointments:
            raise ValueError("You already have an appointment at this time")

        # Check if patient already has an appointment on the same day
        same_day_appointments = self.appointment_repository.find_by_patient_and_date(
            patient_id=patient.id,
            date=appointment_dto.date
        )
        if same_day_appointments:
            raise ValueError("You can only have one appointment per day")

        # Check if the doctor is available at the requested time
        appointments = self.appointment_repository.find_by_doctor_and_date(
            doctor_id=doctor.id, date=appointment_dto.date
        )
        
        # Check for time slot availability
        requested_datetime = datetime.combine(appointment_dto.date, appointment_dto.time)
        for appointment in appointments:
            appointment_datetime = datetime.combine(appointment.date, appointment.time)
            if abs((appointment_datetime - requested_datetime).total_seconds()) < 1800:
                raise ValueError("The doctor is not available at the requested time")

        # Create the appointment
        appointment = Appointment(
            date=appointment_dto.date,
            time=appointment_dto.time,
            status=AppointmentStatus.SCHEDULED,
            patient=patient,
            doctor=doctor,
        )

        # Save the appointment
        saved_appointment = self.appointment_repository.save(appointment)

        # Return the DTO
        return self._to_dto(saved_appointment)
    
    @staticmethod
    def _to_dto(appointment: Appointment) -> AppointmentDTO:
        from medical_system.application.dtos.patient_dto import PatientDTO
        from medical_system.application.dtos.doctor_dto import DoctorDTO
        
        return AppointmentDTO(
            id=appointment.id,
            date=appointment.date,
            time=appointment.time,
            status=str(appointment.status).lower(),
            patient=PatientDTO(
                id=appointment.patient.id,
                name=appointment.patient.name,
                email=str(appointment.patient.email),
                birth_date=appointment.patient.birth_date,
            ),
            doctor=DoctorDTO(
                id=appointment.doctor.id,
                name=appointment.doctor.name,
                email=str(appointment.doctor.email),
                specialty=appointment.doctor.specialty,
            ),
        )
