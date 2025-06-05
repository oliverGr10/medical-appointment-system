import pytest
from unittest.mock import create_autospec
from datetime import date, time, datetime, timedelta
from medical_system.usecases.appointment.create_appointment import CreateAppointmentUseCase
from medical_system.usecases.dtos.appointment_dto import CreateAppointmentDTO
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.appointment import Appointment
from medical_system.domain.value_objects.email import Email
from medical_system.domain.value_objects.reservation_status import AppointmentStatus
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository

class TestCreateAppointmentUseCase:
    
    @pytest.fixture
    def appointment_repo(self):
        return create_autospec(AppointmentRepository, instance=True)
    
    @pytest.fixture
    def patient_repo(self):
        return create_autospec(PatientRepository, instance=True)
    
    @pytest.fixture
    def doctor_repo(self):
        return create_autospec(DoctorRepository, instance=True)
    
    @pytest.fixture
    def patient(self):
        patient = Patient(
            name="Juan Pérez",
            email=Email("juan@example.com"),
            birth_date=date(1990, 1, 1)
        )
        patient.id = 1
        return patient
    
    @pytest.fixture
    def doctor(self):
        doctor = Doctor(
            name="Dr. Carlos García",
            email=Email("dr.garcia@example.com"),
            specialty="Cardiología"
        )
        doctor.id = 1
        return doctor
    
    @pytest.fixture
    def appointment_datetime(self):
        return datetime.now() + timedelta(days=2)
    
    @pytest.fixture
    def appointment_data(self, appointment_datetime):
        return CreateAppointmentDTO(
            patient_id=1,
            doctor_id=1,
            date=appointment_datetime.date(),
            time=time(10, 0)
        )
    
    @pytest.fixture
    def use_case(self, appointment_repo, patient_repo, doctor_repo, patient, doctor):
        patient_repo.find_by_id.return_value = patient
        doctor_repo.find_by_id.return_value = doctor
    
        appointment_repo.find_by_doctor_patient_datetime.return_value = None
        appointment_repo.find_patient_appointments_at_same_time.return_value = []
        appointment_repo.find_by_patient_and_date.return_value = []
        
        return CreateAppointmentUseCase(
            appointment_repository=appointment_repo,
            patient_repository=patient_repo,
            doctor_repository=doctor_repo
        )
    
    def test_should_create_appointment_when_valid_data(
        self, use_case, appointment_repo,
        appointment_data, patient, doctor, appointment_datetime
    ):
        saved_appointment = Appointment(
            date=appointment_datetime.date(),
            time=time(10, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        saved_appointment.id = 1
        appointment_repo.save.return_value = saved_appointment
        
        result = use_case.execute(appointment_data)
        
        assert result.id == 1
        assert result.status == AppointmentStatus.SCHEDULED.value.lower()
        appointment_repo.save.assert_called_once()
    
    def test_should_raise_error_when_patient_not_found(self, use_case, patient_repo, appointment_data):
        patient_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="No se encontró el paciente con ID: 1"):
            use_case.execute(appointment_data)
    
    def test_should_raise_error_when_doctor_not_found(self, use_case, doctor_repo, appointment_data):
        doctor_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="No se encontró el doctor con ID: 1"):
            use_case.execute(appointment_data)
    
    def test_should_raise_error_when_duplicate_appointment(
        self, use_case, appointment_repo, appointment_data, patient, doctor, appointment_datetime
    ):
        existing_appointment = Appointment(
            date=appointment_datetime.date(),
            time=time(10, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        existing_appointment.id = 1
        appointment_repo.find_by_doctor_patient_datetime.return_value = existing_appointment
        
        with pytest.raises(ValueError, match="Ya existe una cita idéntica"):
            use_case.execute(appointment_data)
    
    def test_should_raise_error_when_patient_has_appointment_same_time(
        self, use_case, appointment_repo, appointment_data, patient, doctor, appointment_datetime
    ):
        same_time_appointment = Appointment(
            date=appointment_datetime.date(),
            time=time(10, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        same_time_appointment.id = 2
        
        appointment_repo.find_patient_appointments_at_same_time.return_value = [same_time_appointment]
        
        with pytest.raises(ValueError, match="Ya tienes una cita programada a esta misma hora"):
            use_case.execute(appointment_data)
    
    def test_should_raise_error_when_patient_has_appointment_same_day(
        self, use_case, appointment_repo, appointment_data, patient, doctor, appointment_datetime
    ):
        same_day_appointment = Appointment(
            date=appointment_datetime.date(),
            time=time(14, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        same_day_appointment.id = 2
        
        appointment_repo.find_by_patient_and_date.return_value = [same_day_appointment]
        
        with pytest.raises(ValueError, match="Solo puedes tener una cita por día"):
            use_case.execute(appointment_data)
