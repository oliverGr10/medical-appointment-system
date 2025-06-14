import pytest
from datetime import date, time
from unittest.mock import create_autospec
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.patient import Patient
from medical_system.domain.ports.repositories.appointment_repository import AppointmentRepository
from medical_system.domain.value_objects.email import Email
from medical_system.usecases.appointment.list_all_appointments import ListAllAppointmentsUseCase

class TestListAllAppointmentsUseCase:
    
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
    def use_case(self, appointment_repo):
        return ListAllAppointmentsUseCase(appointment_repo)
    
    def test_should_return_all_appointments_when_exist(
        self, use_case, appointment_repo, scheduled_appointment, completed_appointment
    ):
        appointments = [scheduled_appointment, completed_appointment]
        appointments.sort(key=lambda x: (x.date, x.time))
        appointment_repo.find_all.return_value = appointments
        
        result = use_case.execute()
        
        assert len(result) == 2
        result_ids = {r['id'] for r in result}
        assert result_ids == {1, 2}
        statuses = {r['status'] for r in result}
        assert "Programada" in statuses
        assert "Completada" in statuses
        appointment_repo.find_all.assert_called_once()
    
    def test_should_return_empty_list_when_no_appointments(self, use_case, appointment_repo):
        appointment_repo.find_all.return_value = []
        
        result = use_case.execute()
        
        assert len(result) == 0
        appointment_repo.find_all.assert_called_once()
    
    def test_should_return_appointments_with_different_statuses(
        self, use_case, appointment_repo, scheduled_appointment, 
        completed_appointment, cancelled_appointment
    ):
        appointments = [
            scheduled_appointment, 
            completed_appointment,
            cancelled_appointment
        ]
        appointments.sort(key=lambda x: (x.date, x.time))
        appointment_repo.find_all.return_value = appointments
        
        result = use_case.execute()
        
        assert len(result) == 3
        result_ids = {r['id'] for r in result}
        assert result_ids == {1, 2, 3}
        statuses = {r['status'] for r in result}
        assert "Programada" in statuses
        assert "Completada" in statuses
        assert "Cancelada" in statuses
        appointment_repo.find_all.assert_called_once()
    
    def test_should_filter_appointments_by_status(
        self, use_case, appointment_repo, scheduled_appointment, completed_appointment, cancelled_appointment
    ):
        from medical_system.domain.entities.appointment import AppointmentStatus

        appointment_repo.find_all.return_value = [
            scheduled_appointment,
            completed_appointment,
            cancelled_appointment
        ]
        result = use_case.execute(status="scheduled")
        
        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['status'] == "Programada"
        
        appointment_repo.find_all.assert_called_once()
