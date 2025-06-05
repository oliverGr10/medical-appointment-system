import pytest
from unittest.mock import create_autospec
from datetime import date, time, timedelta
from medical_system.usecases.appointment.complete_appointment import CompleteAppointmentUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository

class TestCompleteAppointmentUseCase:
    
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
        appointment_repo.save.return_value = appointment
        return CompleteAppointmentUseCase(appointment_repo)
    
    def test_should_complete_appointment_when_valid_data(self, use_case, appointment_repo, appointment):
        from medical_system.domain.entities.appointment import AppointmentStatus
        
        result = use_case.execute(appointment_id=1, doctor_id=1)
        
        assert result.id == 1
        assert result.status == AppointmentStatus.COMPLETED
        assert appointment.status == AppointmentStatus.COMPLETED
        appointment_repo.save.assert_called_once_with(appointment)
    
    def test_should_raise_error_when_appointment_not_found(self, use_case, appointment_repo):
        appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="No se encontró la cita especificada"):
            use_case.execute(appointment_id=999, doctor_id=1)
        
        appointment_repo.find_by_id.assert_called_once_with(999)
    
    def test_should_raise_error_when_unauthorized_doctor(self, use_case, appointment_repo):
        with pytest.raises(UnauthorizedError, match="Solo puedes completar tus propias citas"):
            use_case.execute(appointment_id=1, doctor_id=2)

        appointment_repo.find_by_id.assert_called_once_with(1)
    
    def test_should_raise_error_when_appointment_already_completed(self, use_case, appointment, appointment_repo):
        from medical_system.domain.entities.appointment import AppointmentStatus
        appointment.status = AppointmentStatus.COMPLETED
        
        with pytest.raises(ValueError, match="La cita ya está completada"):
            use_case.execute(appointment_id=1, doctor_id=1)
        
        appointment_repo.save.assert_not_called()
    
    def test_should_raise_error_when_appointment_cancelled(self, use_case, appointment, appointment_repo):
        from medical_system.domain.entities.appointment import AppointmentStatus
        appointment.status = AppointmentStatus.CANCELLED
        
        with pytest.raises(ValueError, match="No se puede completar una cita cancelada"):
            use_case.execute(appointment_id=1, doctor_id=1)
        
        appointment_repo.save.assert_not_called()
