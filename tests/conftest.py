from datetime import date, time, timedelta
import pytest
from medical_system.domain.entities.appointment import Appointment
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.patient import Patient
from medical_system.domain.value_objects.email import Email
from medical_system.domain.value_objects.reservation_status import AppointmentStatus

@pytest.fixture
def sample_patient():

    return Patient(
        name="Juan Pérez",
        email=Email("juan@example.com"),
        birth_date=date(1990, 1, 1)
    )


@pytest.fixture
def another_patient():
    """Crea otro paciente de ejemplo para pruebas."""
    return Patient(
        name="María López",
        email=Email("maria@example.com"),
        birth_date=date(1985, 5, 15)
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
def another_doctor():
    """Crea otro doctor de ejemplo para pruebas."""
    return Doctor(
        name="Dra. Ana Martínez",
        email=Email("dra.martinez@example.com"),
        specialty="Pediatría"
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
def completed_appointment(sample_patient, sample_doctor):
    """Crea una cita completada para pruebas."""
    return Appointment(
        date=date.today() - timedelta(days=1),  # Ayer
        time=time(14, 30),
        status=AppointmentStatus.COMPLETED,
        patient=sample_patient,
        doctor=sample_doctor
    )


@pytest.fixture
def cancelled_appointment(sample_patient, sample_doctor):
    """Crea una cita cancelada para pruebas."""
    return Appointment(
        date=date.today() + timedelta(days=2),
        time=time(11, 0),
        status=AppointmentStatus.CANCELLED,
        patient=sample_patient,
        doctor=sample_doctor
    )

@pytest.fixture
def tomorrow():
    """Retorna la fecha de mañana."""
    return date.today() + timedelta(days=1)


@pytest.fixture
def yesterday():
    """Retorna la fecha de ayer."""
    return date.today() - timedelta(days=1)


@pytest.fixture
def next_week():
    """Retorna la fecha de la próxima semana."""
    return date.today() + timedelta(weeks=1)


@pytest.fixture
def next_month():
    """Retorna la fecha del próximo mes."""
    today = date.today()
    if today.month == 12:
        return today.replace(year=today.year + 1, month=1)
    return today.replace(month=today.month + 1)
