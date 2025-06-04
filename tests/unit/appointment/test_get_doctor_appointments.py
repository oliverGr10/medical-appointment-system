import pytest
from unittest.mock import MagicMock
from datetime import date, time
from medical_system.application.use_cases.appointment.get_doctor_appointments import GetDoctorAppointmentsUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestGetDoctorAppointmentsUseCase:
    """Pruebas para el caso de uso de obtención de citas de un doctor."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.appointment_repo = MagicMock()
        self.doctor_repo = MagicMock()
        self.use_case = GetDoctorAppointmentsUseCase(
            appointment_repository=self.appointment_repo,
            doctor_repository=self.doctor_repo
        )
        
        # Crear paciente de prueba
        self.patient = Patient(
            name="Juan Pérez",
            email=Email("juan@example.com"),
            birth_date=date(1990, 1, 1)
        )
        self.patient.id = 1
        
        # Crear doctor de prueba
        self.doctor = Doctor(
            name="Dr. Ana López",
            email=Email("ana@example.com"),
            specialty="Cardiología"
        )
        self.doctor.id = 1
        
        # Configurar repositorios
        self.doctor_repo.find_by_id.return_value = self.doctor
        
        # Configurar fecha de prueba
        self.test_date = date(2025, 6, 10)
        
        return self
    
    def test_get_doctor_appointments_success(self, setup):
        """Prueba la obtención exitosa de las citas de un doctor."""
        # Configurar citas de prueba
        appointments = [
            Appointment(
                date=self.test_date,
                time=time(10, 0),
                patient=self.patient,
                doctor=self.doctor,
                status=AppointmentStatus.SCHEDULED
            ),
            Appointment(
                date=self.test_date,
                time=time(14, 0),
                patient=self.patient,
                doctor=self.doctor,
                status=AppointmentStatus.SCHEDULED
            )
        ]
        appointments[0].id = 1
        appointments[1].id = 2
        
        self.appointment_repo.find_by_doctor_and_date.return_value = appointments
        
        # Ejecutar
        result = self.use_case.execute(
            doctor_id=1,
            request_date=self.test_date,
            requesting_doctor_id=1
        )
        
        # Verificar
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        self.appointment_repo.find_by_doctor_and_date.assert_called_once_with(
            doctor_id=1,
            date=self.test_date
        )
    
    def test_get_doctor_appointments_unauthorized(self, setup):
        """Prueba cuando un doctor intenta ver las citas de otro doctor."""
        with pytest.raises(UnauthorizedError, match="You can only view your own appointments"):
            self.use_case.execute(
                doctor_id=1,
                request_date=self.test_date,
                requesting_doctor_id=2  # ID de doctor diferente
            )
    
    def test_get_doctor_appointments_doctor_not_found(self, setup):
        """Prueba cuando el doctor no existe."""
        self.doctor_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Doctor not found"):
            self.use_case.execute(
                doctor_id=999,
                request_date=self.test_date,
                requesting_doctor_id=999
            )
    
    def test_get_doctor_appointments_empty(self, setup):
        """Prueba cuando el doctor no tiene citas para la fecha especificada."""
        self.appointment_repo.find_by_doctor_and_date.return_value = []
        
        # Ejecutar
        result = self.use_case.execute(
            doctor_id=1,
            request_date=self.test_date,
            requesting_doctor_id=1
        )
        
        # Verificar
        assert len(result) == 0
        self.appointment_repo.find_by_doctor_and_date.assert_called_once_with(
            doctor_id=1,
            date=self.test_date
        )
