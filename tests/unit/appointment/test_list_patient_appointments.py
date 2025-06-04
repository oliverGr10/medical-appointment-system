import pytest
from unittest.mock import MagicMock
from datetime import date, time
from medical_system.application.use_cases.appointment.list_patient_appointments import ListPatientAppointmentsUseCase
from medical_system.domain.entities.appointment import Appointment, AppointmentStatus
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestListPatientAppointmentsUseCase:
    """Pruebas para el caso de uso de listado de citas de un paciente."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.appointment_repo = MagicMock()
        self.patient_repo = MagicMock()
        self.use_case = ListPatientAppointmentsUseCase(
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
        
        # Configurar repositorios
        self.patient_repo.find_by_id.return_value = self.patient
        
        # Configurar fecha de prueba
        self.test_date = date(2025, 6, 10)
        
        return self
    
    def test_list_patient_appointments_success(self, setup):
        """Prueba la obtención exitosa de las citas de un paciente."""
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
        
        self.appointment_repo.find_by_patient.return_value = appointments
        
        # Ejecutar
        result = self.use_case.execute(
            patient_id=1,
            requesting_patient_id=1
        )
        
        # Verificar
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        self.appointment_repo.find_by_patient.assert_called_once_with(1)
    
    def test_list_patient_appointments_unauthorized(self, setup):
        """Prueba cuando un paciente intenta ver las citas de otro paciente."""
        with pytest.raises(UnauthorizedError, match="You can only view your own appointments"):
            self.use_case.execute(
                patient_id=1,
                requesting_patient_id=2  # ID de paciente diferente
            )
    
    def test_list_patient_appointments_patient_not_found(self, setup):
        """Prueba cuando el paciente no existe."""
        self.patient_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Patient not found"):
            self.use_case.execute(
                patient_id=999,
                requesting_patient_id=999
            )
    
    def test_list_patient_appointments_empty(self, setup):
        """Prueba cuando el paciente no tiene citas."""
        self.appointment_repo.find_by_patient.return_value = []
        
        # Ejecutar
        result = self.use_case.execute(
            patient_id=1,
            requesting_patient_id=1
        )
        
        # Verificar
        assert len(result) == 0
        self.appointment_repo.find_by_patient.assert_called_once_with(1)
    
    def test_list_patient_appointments_with_different_statuses(self, setup):
        """Prueba que se devuelven citas con diferentes estados."""
        # Configurar citas con diferentes estados
        appointments = [
            Appointment(
                date=self.test_date,
                time=time(9, 0),
                patient=self.patient,
                doctor=self.doctor,
                status=AppointmentStatus.SCHEDULED
            ),
            Appointment(
                date=self.test_date,
                time=time(10, 0),
                patient=self.patient,
                doctor=self.doctor,
                status=AppointmentStatus.CANCELLED
            ),
            Appointment(
                date=self.test_date,
                time=time(11, 0),
                patient=self.patient,
                doctor=self.doctor,
                status=AppointmentStatus.COMPLETED
            )
        ]
        
        for i, apt in enumerate(appointments, 1):
            apt.id = i
        
        self.appointment_repo.find_by_patient.return_value = appointments
        
        # Ejecutar
        result = self.use_case.execute(
            patient_id=1,
            requesting_patient_id=1
        )
        
        # Verificar
        assert len(result) == 3
        assert result[0].status == "scheduled"
        assert result[1].status == "cancelled"
        assert result[2].status == "completed"
