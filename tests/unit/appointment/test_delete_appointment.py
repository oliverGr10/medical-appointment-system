import pytest
from unittest.mock import create_autospec
from datetime import date, time, timedelta
from medical_system.usecases.appointment.delete_appointment import DeleteAppointmentUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.repositories.appointment_repository import AppointmentRepository

class TestDeleteAppointmentUseCase:
    
    @pytest.fixture
    def appointment_repo(self):
        return create_autospec(AppointmentRepository, instance=True)
    
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
    def appointment(self, patient, doctor):
        future_date = date.today() + timedelta(days=1)
        appointment = Appointment(
            date=future_date,
            time=time(10, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        appointment.id = 1
        return appointment
    
    @pytest.fixture
    def use_case(self, appointment_repo, appointment):
        appointment_repo.find_by_id.return_value = appointment
        return DeleteAppointmentUseCase(appointment_repo)
    
    def test_should_delete_appointment_when_admin(self, use_case, appointment_repo):
        use_case.execute(appointment_id=1, is_admin=True)
        appointment_repo.delete.assert_called_once_with(1)
    
    def test_should_raise_error_when_appointment_not_found(self, use_case, appointment_repo):
        appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Appointment not found"):
            use_case.execute(appointment_id=999, is_admin=True)
    
    def test_should_raise_error_when_not_admin(self, use_case):
        with pytest.raises(UnauthorizedError, match="Only administrators can delete appointments"):
            use_case.execute(appointment_id=1, is_admin=False)
    
    def test_should_delete_completed_appointment_when_admin(self, use_case, appointment_repo, appointment):
        appointment.complete()
        
        use_case.execute(appointment_id=1, is_admin=True)
        appointment_repo.delete.assert_called_once_with(1)
    
    def test_should_delete_cancelled_appointment_when_admin(self, use_case, appointment_repo, appointment):
        appointment.cancel()
        
        use_case.execute(appointment_id=1, is_admin=True)
        appointment_repo.delete.assert_called_once_with(1)
