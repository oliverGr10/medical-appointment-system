from datetime import date, time
from unittest.mock import create_autospec
import pytest
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.patient import Patient
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository
from medical_system.domain.value_objects.email import Email
from medical_system.usecases.appointment.get_doctor_appointments import GetDoctorAppointmentsUseCase


class TestGetDoctorAppointmentsUseCase:
    
    @pytest.fixture
    def appointment_repo(self):
        return create_autospec(AppointmentRepository, instance=True)
    
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
            name="Dr. Ana López",
            email=Email("ana@example.com"),
            specialty="Cardiología"
        )
        doctor.id = 1
        return doctor
    
    @pytest.fixture
    def test_date(self):
        return date(2025, 6, 10)
    
    @pytest.fixture
    def appointments(self, test_date, patient, doctor):
        appt1 = Appointment(
            date=test_date,
            time=time(10, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        appt1.id = 1
        
        appt2 = Appointment(
            date=test_date,
            time=time(14, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        appt2.id = 2
        
        return [appt1, appt2]
    
    @pytest.fixture
    def use_case(self, appointment_repo, doctor_repo, doctor):
        doctor_repo.find_by_id.return_value = doctor
        return GetDoctorAppointmentsUseCase(appointment_repo, doctor_repo)
    
    def test_should_return_appointments_when_doctor_exists_and_authorized(
        self, use_case, appointment_repo, appointments, test_date
    ):
        appointment_repo.find_by_doctor_and_date.return_value = appointments
        
        result = use_case.execute(
            doctor_id=1,
            request_date=test_date,
            requesting_doctor_id=1
        )
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        appointment_repo.find_by_doctor_and_date.assert_called_once_with(
            doctor_id=1,
            date=test_date
        )
    
    def test_should_raise_error_when_unauthorized_doctor(self, use_case, test_date):
        with pytest.raises(UnauthorizedError, match="You can only view your own appointments"):
            use_case.execute(
                doctor_id=1,
                request_date=test_date,
                requesting_doctor_id=2
            )
    
    def test_should_raise_error_when_doctor_not_found(self, use_case, doctor_repo, test_date):
        doctor_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Doctor not found"):
            use_case.execute(
                doctor_id=999,
                request_date=test_date,
                requesting_doctor_id=999
            )
    
    def test_should_return_empty_list_when_no_appointments(
        self, use_case, appointment_repo, test_date
    ):
        appointment_repo.find_by_doctor_and_date.return_value = []
        
        result = use_case.execute(
            doctor_id=1,
            request_date=test_date,
            requesting_doctor_id=1
        )
        
        assert len(result) == 0
        appointment_repo.find_by_doctor_and_date.assert_called_once_with(
            doctor_id=1,
            date=test_date
        )
