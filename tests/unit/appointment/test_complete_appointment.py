import pytest
from unittest.mock import MagicMock
from datetime import date, time, timedelta
from medical_system.application.use_cases.appointment.complete_appointment import CompleteAppointmentUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestCompleteAppointmentUseCase:
    """Pruebas para el caso de uso de completar una cita."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.appointment_repo = MagicMock()
        self.use_case = CompleteAppointmentUseCase(
            appointment_repository=self.appointment_repo
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
        
        # Crear cita de prueba (usando una fecha futura)
        future_date = date.today() + timedelta(days=1)
        self.appointment = Appointment(
            date=future_date,
            time=time(10, 0),
            patient=self.patient,
            doctor=self.doctor,
            status=AppointmentStatus.SCHEDULED
        )
        self.appointment.id = 1
        
        # Configurar repositorios
        self.appointment_repo.find_by_id.return_value = self.appointment
        self.appointment_repo.save.return_value = self.appointment
        
        return self
    
    def test_complete_appointment_success(self, setup):
        """Prueba la finalización exitosa de una cita."""
        # Ejecutar
        result = self.use_case.execute(appointment_id=1, doctor_id=1)
        
        # Verificar
        assert result.id == 1
        assert result.status == "completed"
        assert self.appointment.status == AppointmentStatus.COMPLETED
        self.appointment_repo.save.assert_called_once_with(self.appointment)
    
    def test_complete_appointment_not_found(self, setup):
        """Prueba cuando la cita no existe."""
        self.appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Appointment not found"):
            self.use_case.execute(appointment_id=999, doctor_id=1)
    
    def test_complete_appointment_unauthorized(self, setup):
        """Prueba cuando un doctor intenta completar una cita que no es suya."""
        with pytest.raises(UnauthorizedError, match="You can only complete your own appointments"):
            self.use_case.execute(appointment_id=1, doctor_id=2)  # ID de doctor diferente
    
    def test_complete_already_completed_appointment(self, setup):
        """Prueba cuando se intenta completar una cita ya completada."""
        # Configurar cita ya completada
        self.appointment.complete()
        
        # Debería lanzar una excepción
        with pytest.raises(ValueError, match="Appointment is already completed"):
            self.use_case.execute(appointment_id=1, doctor_id=1)
        
        # No debería llamar a save porque hubo un error
        self.appointment_repo.save.assert_not_called()
    
    def test_complete_cancelled_appointment(self, setup):
        """Prueba cuando se intenta completar una cita cancelada."""
        # Configurar cita cancelada
        self.appointment.cancel()
        
        with pytest.raises(ValueError, match="Cannot complete a cancelled appointment"):
            self.use_case.execute(appointment_id=1, doctor_id=1)
