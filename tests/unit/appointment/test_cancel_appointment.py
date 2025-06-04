import pytest
from unittest.mock import MagicMock
from datetime import date, time, timedelta
from medical_system.application.use_cases.appointment.cancel_appointment import CancelAppointmentUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestCancelAppointmentUseCase:
    """Pruebas para el caso de uso de cancelación de cita."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.appointment_repo = MagicMock()
        self.patient_repo = MagicMock()
        self.use_case = CancelAppointmentUseCase(
            appointment_repository=self.appointment_repo,
            patient_repository=self.patient_repo
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
        self.patient_repo.find_by_id.return_value = self.patient
        
        return self
    
    def test_cancel_appointment_success(self, setup):
        """Prueba la cancelación exitosa de una cita."""
        # Ejecutar
        self.use_case.execute(appointment_id=1, patient_id=1)
        
        # Verificar
        assert self.appointment.status == AppointmentStatus.CANCELLED
        self.appointment_repo.save.assert_called_once_with(self.appointment)
    
    def test_cancel_appointment_not_found(self, setup):
        """Prueba cuando la cita no existe."""
        self.appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Appointment not found"):
            self.use_case.execute(appointment_id=999, patient_id=1)
    
    def test_cancel_appointment_unauthorized(self, setup):
        """Prueba cuando un paciente intenta cancelar la cita de otro paciente."""
        with pytest.raises(UnauthorizedError, match="You can only cancel your own appointments"):
            self.use_case.execute(appointment_id=1, patient_id=2)  # ID de paciente diferente
    
    def test_cancel_already_cancelled_appointment(self, setup):
        """Prueba cuando se intenta cancelar una cita ya cancelada."""
        # Configurar cita ya cancelada
        self.appointment.cancel()
        
        # Verificar que no se puede cancelar nuevamente
        with pytest.raises(ValueError, match="Appointment is already cancelled"):
            self.use_case.execute(appointment_id=1, patient_id=1)
    
    def test_cancel_completed_appointment(self, setup):
        """Prueba cuando se intenta cancelar una cita ya completada."""
        # Configurar cita completada
        self.appointment.complete()
        
        with pytest.raises(ValueError, match="Cannot cancel a completed appointment"):
            self.use_case.execute(appointment_id=1, patient_id=1)
