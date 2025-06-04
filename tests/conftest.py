"""
Fixtures y configuraciones comunes para todas las pruebas.
"""
import pytest
from datetime import date, time, datetime, timedelta
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.appointment import Appointment
from medical_system.domain.value_objects.email import Email
from medical_system.domain.value_objects.reservation_status import AppointmentStatus

@pytest.fixture
def sample_patient():
    """Crea un paciente de ejemplo para pruebas."""
    return Patient(
        name="Juan Pérez",
        email=Email("juan@example.com"),
        birth_date=date(1990, 1, 1)
    )

@pytest.fixture
def sample_doctor():
    """Crea un doctor de ejemplo para pruebas."""
    return Doctor(
        name="Dr. Carlos García",
        email=Email("dr.garcia@example.com"),
        specialty="Cardiología"
    )

@pytest.fixture
def sample_appointment(sample_patient, sample_doctor):
    """Crea una cita de ejemplo para pruebas."""
    return Appointment(
        date=date.today() + timedelta(days=1),  # Mañana
        time=time(10, 0),  # 10:00 AM
        status=AppointmentStatus.SCHEDULED,
        patient=sample_patient,
        doctor=sample_doctor
    )

@pytest.fixture
def tomorrow():
    """Retorna la fecha de mañana."""
    return date.today() + timedelta(days=1)
