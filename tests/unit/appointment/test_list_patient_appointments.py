from datetime import date, time
from unittest.mock import create_autospec
import pytest
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.patient import Patient
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.domain.value_objects.email import Email
from medical_system.usecases.appointment.list_patient_appointments import ListPatientAppointmentsUseCase

class TestListPatientAppointmentsUseCase:
    
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
    def test_date(self):
        return date(2025, 6, 10)
    
    @pytest.fixture
    def scheduled_appointment(self, test_date, patient, doctor):
        appointment = Appointment(
            date=test_date,
            time=time(10, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.SCHEDULED
        )
        appointment.id = 1
        return appointment
    
    @pytest.fixture
    def completed_appointment(self, test_date, patient, doctor):
        appointment = Appointment(
            date=test_date,
            time=time(14, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.COMPLETED
        )
        appointment.id = 2
        return appointment
    
    @pytest.fixture
    def cancelled_appointment(self, test_date, patient, doctor):
        appointment = Appointment(
            date=test_date,
            time=time(9, 0),
            patient=patient,
            doctor=doctor,
            status=AppointmentStatus.CANCELLED
        )
        appointment.id = 3
        return appointment
    
    @pytest.fixture
    def use_case(self, appointment_repo, patient_repo, patient):
        patient_repo.find_by_id.return_value = patient
        return ListPatientAppointmentsUseCase(appointment_repo, patient_repo)
    
    def test_should_return_patient_appointments_when_authorized(
        self, use_case, appointment_repo, scheduled_appointment, completed_appointment
    ):
        appointment_repo.find_by_patient.return_value = [scheduled_appointment, completed_appointment]
        
        result = use_case.execute(patient_id=1, requesting_patient_id=1)
        
        assert len(result) == 2
        result_ids = [appt['id'] for appt in result]
        assert 1 in result_ids
        assert 2 in result_ids
        appointment_repo.find_by_patient.assert_called_once_with(patient_id=1)
    
    def test_should_raise_error_when_unauthorized_patient(self, use_case):
        with pytest.raises(UnauthorizedError, match="You can only view your own appointments"):
            use_case.execute(patient_id=1, requesting_patient_id=2)
    
    def test_should_raise_error_when_patient_not_found(self, use_case, patient_repo):
        patient_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Patient not found"):
            use_case.execute(patient_id=999, requesting_patient_id=999)
    
    def test_should_return_empty_list_when_no_appointments(self, use_case, appointment_repo):
        appointment_repo.find_by_patient.return_value = []
        
        result = use_case.execute(patient_id=1, requesting_patient_id=1)
        
        assert len(result) == 0
        appointment_repo.find_by_patient.assert_called_once_with(patient_id=1)
    
    def test_should_return_appointments_with_different_statuses(
        self, use_case, appointment_repo, scheduled_appointment,
        completed_appointment, cancelled_appointment
    ):
        appointment_repo.find_by_patient.return_value = [
            scheduled_appointment,
            cancelled_appointment,
            completed_appointment
        ]
        
        result = use_case.execute(patient_id=1, requesting_patient_id=1)
        
        assert len(result) == 3
        statuses = [appt['status'] for appt in result]
        assert "scheduled" in statuses
        assert "cancelled" in statuses
        assert "completed" in statuses
