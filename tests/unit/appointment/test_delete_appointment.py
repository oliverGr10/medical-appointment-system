import pytest
from unittest.mock import MagicMock
from datetime import date, time, timedelta
from medical_system.application.use_cases.appointment.delete_appointment import DeleteAppointmentUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestDeleteAppointmentUseCase:
    """Pruebas para el caso de uso de eliminación de cita."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.appointment_repo = MagicMock()
        self.use_case = DeleteAppointmentUseCase(
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
        
        return self
    
    def test_delete_appointment_success(self, setup):
        """Prueba la eliminación exitosa de una cita por un administrador."""
        # Ejecutar como administrador
        self.use_case.execute(appointment_id=1, is_admin=True)
        
        # Verificar que se llamó al método de eliminación
        self.appointment_repo.delete.assert_called_once_with(1)
    
    def test_delete_appointment_not_found(self, setup):
        """Prueba cuando la cita no existe."""
        self.appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Appointment not found"):
            self.use_case.execute(appointment_id=999, is_admin=True)
    
    def test_delete_appointment_unauthorized(self, setup):
        """Prueba cuando un usuario no administrador intenta eliminar una cita."""
        with pytest.raises(UnauthorizedError, match="Only administrators can delete appointments"):
            self.use_case.execute(appointment_id=1, is_admin=False)
    
    def test_delete_completed_appointment(self, setup):
        """Prueba cuando se intenta eliminar una cita ya completada."""
        # Configurar cita completada
        self.appointment.complete()
        
        # Debería permitir la eliminación incluso si está completada
        self.use_case.execute(appointment_id=1, is_admin=True)
        self.appointment_repo.delete.assert_called_once_with(1)
    
    def test_delete_cancelled_appointment(self, setup):
        """Prueba cuando se intenta eliminar una cita cancelada."""
        # Configurar cita cancelada
        self.appointment.cancel()
        
        # Debería permitir la eliminación incluso si está cancelada
        self.use_case.execute(appointment_id=1, is_admin=True)
        self.appointment_repo.delete.assert_called_once_with(1)
