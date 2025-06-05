import pytest
from unittest.mock import create_autospec
from datetime import date, time, timedelta
from medical_system.usecases.appointment.cancel_appointment import CancelAppointmentUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository

class TestCancelAppointmentUseCase:
    
    @pytest.fixture
    def appointment_repo(self):
        return create_autospec(AppointmentRepository, instance=True)
    
    @pytest.fixture
    def patient_repo(self):
        return create_autospec(PatientRepository, instance=True)
    
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
    def scheduled_appointment(self, patient, doctor):
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
    def use_case(self, appointment_repo, patient_repo, scheduled_appointment, patient):
        appointment_repo.find_by_id.return_value = scheduled_appointment
        patient_repo.find_by_id.return_value = patient
        return CancelAppointmentUseCase(
            appointment_repository=appointment_repo,
            patient_repository=patient_repo
        )
    
    def test_should_cancel_appointment_when_patient_is_owner(self, use_case, appointment_repo, scheduled_appointment):
        use_case.execute(appointment_id=1, patient_id=1)
        
        assert scheduled_appointment.status == AppointmentStatus.CANCELLED
        appointment_repo.save.assert_called_once_with(scheduled_appointment)
    
    def test_should_raise_error_when_appointment_not_found(self, use_case, appointment_repo):
        appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="No se encontró la cita especificada"):
            use_case.execute(appointment_id=999, patient_id=1)
    
    def test_should_raise_error_when_patient_not_owner(self, use_case):
        with pytest.raises(UnauthorizedError, match="Solo puedes cancelar tus propias citas"):
            use_case.execute(appointment_id=1, patient_id=2)
    
    def test_should_raise_error_when_appointment_already_cancelled(self, use_case, scheduled_appointment):
        scheduled_appointment.cancel()
        
        with pytest.raises(ValueError, match="La cita ya está cancelada"):
            use_case.execute(appointment_id=1, patient_id=1)
    
    def test_should_raise_error_when_appointment_completed(self, use_case, scheduled_appointment):
        scheduled_appointment.complete()
        
        with pytest.raises(ValueError, match="No se puede cancelar una cita completada"):
            use_case.execute(appointment_id=1, patient_id=1)
