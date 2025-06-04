"""
Pruebas unitarias para el caso de uso CreateAppointmentUseCase.
"""
import pytest
from unittest.mock import MagicMock
from datetime import date, time, datetime, timedelta
from medical_system.application.use_cases.appointment.create_appointment import CreateAppointmentUseCase
from medical_system.application.dtos.appointment_dto import CreateAppointmentDTO
from medical_system.domain.entities.patient import Patient
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.entities.appointment import Appointment
from medical_system.domain.value_objects.email import Email
from medical_system.domain.value_objects.reservation_status import AppointmentStatus

class TestCreateAppointmentUseCase:
    """Pruebas para el caso de uso de creación de citas."""
    
    @pytest.fixture
    def setup(self):
        # Configurar mocks
        self.appointment_repo = MagicMock()
        self.patient_repo = MagicMock()
        self.doctor_repo = MagicMock()
        
        # Configurar paciente
        self.patient = Patient(
            name="Juan Pérez",
            email=Email("juan@example.com"),
            birth_date=date(1990, 1, 1)
        )
        self.patient.id = 1
        self.patient_repo.find_by_id.return_value = self.patient
        
        # Configurar doctor
        self.doctor = Doctor(
            name="Dr. Carlos García",
            email=Email("dr.garcia@example.com"),
            specialty="Cardiología"
        )
        self.doctor.id = 1
        self.doctor_repo.find_by_id.return_value = self.doctor
        
        # Configurar cita existente (usando una fecha futura)
        future_date = datetime.now() + timedelta(days=2)
        self.appointment_datetime = datetime(
            year=future_date.year,
            month=future_date.month,
            day=future_date.day,
            hour=10,
            minute=0
        )
        self.existing_appointment = Appointment(
            date=self.appointment_datetime.date(),
            time=self.appointment_datetime.time(),
            patient=self.patient,
            doctor=self.doctor,
            status=AppointmentStatus.SCHEDULED
        )
        self.existing_appointment.id = 1
        self.appointment_repo.find_by_patient_and_date.return_value = []
        self.appointment_repo.find_by_doctor_and_date.return_value = []
        
        # Crear caso de uso
        self.use_case = CreateAppointmentUseCase(
            appointment_repository=self.appointment_repo,
            patient_repository=self.patient_repo,
            doctor_repository=self.doctor_repo
        )
        
        # Datos de la cita (usando una fecha futura)
        future_date = date.today() + timedelta(days=2)
        self.tomorrow = future_date
        self.appointment_data = CreateAppointmentDTO(
            patient_id=1,
            doctor_id=1,
            date=future_date,
            time=time(10, 0)  # 10:00 AM
        )
    
    def test_create_appointment_success(self, setup):
        """Prueba la creación exitosa de una cita."""
        # Configurar el guardado exitoso
        appointment_datetime = datetime.combine(self.tomorrow, time(10, 0))
        saved_appointment = Appointment(
            date=appointment_datetime.date(),
            time=appointment_datetime.time(),
            patient=self.patient,
            doctor=self.doctor,
            status=AppointmentStatus.SCHEDULED
        )
        saved_appointment.id = 1
        self.appointment_repo.save.return_value = saved_appointment
        
        # Configurar que no hay citas duplicadas
        self.appointment_repo.find_by_doctor_patient_datetime.return_value = None
        self.appointment_repo.find_patient_appointments_at_same_time.return_value = []
        
        # Ejecutar
        result = self.use_case.execute(self.appointment_data)
        
        # Verificar
        assert result.id == 1
        self.appointment_repo.save.assert_called_once()
        self.appointment_repo.find_by_doctor_patient_datetime.assert_called_once()
        self.appointment_repo.find_patient_appointments_at_same_time.assert_called_once()
    
    def test_create_appointment_patient_not_found(self, setup):
        """Prueba cuando el paciente no existe."""
        self.patient_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Patient not found"):
            self.use_case.execute(self.appointment_data)
    
    def test_create_appointment_doctor_not_found(self, setup):
        """Prueba cuando el doctor no existe."""
        self.doctor_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Doctor not found"):
            self.use_case.execute(self.appointment_data)
    
    def test_create_appointment_duplicate(self, setup):
        """Prueba cuando la cita ya existe."""
        # Configurar que ya existe una cita con el mismo doctor, paciente, fecha y hora
        self.appointment_repo.find_by_doctor_patient_datetime.return_value = self.existing_appointment
        
        with pytest.raises(ValueError, match="This appointment already exists"):
            self.use_case.execute(self.appointment_data)
    
    def test_create_appointment_same_time(self, setup):
        """Prueba cuando el paciente ya tiene una cita a la misma hora."""
        # Configurar que hay una cita a la misma hora
        appointment_datetime = datetime.combine(self.tomorrow, time(10, 0))
        same_time_appointment = Appointment(
            date=appointment_datetime.date(),
            time=appointment_datetime.time(),
            patient=self.patient,
            doctor=self.doctor,  # Mismo doctor
            status=AppointmentStatus.SCHEDULED
        )
        same_time_appointment.id = 2
        
        # Configurar que no hay cita duplicada para que pase a la siguiente validación
        self.appointment_repo.find_by_doctor_patient_datetime.return_value = None
        
        # Configurar que hay una cita a la misma hora
        self.appointment_repo.find_patient_appointments_at_same_time.return_value = [same_time_appointment]
        
        # Verificar que se lanza la excepción correcta
        with pytest.raises(ValueError, match="You already have an appointment at this time"):
            self.use_case.execute(self.appointment_data)
    
    def test_create_appointment_same_day(self, setup):
        """Prueba cuando el paciente ya tiene una cita el mismo día."""
        # Configurar que hay una cita el mismo día pero a diferente hora
        same_day_datetime = datetime.combine(self.tomorrow, time(14, 0))
        same_day_appointment = Appointment(
            date=same_day_datetime.date(),
            time=same_day_datetime.time(),
            patient=self.patient,
            doctor=self.doctor,
            status=AppointmentStatus.SCHEDULED
        )
        same_day_appointment.id = 2
        
        # Configurar que no hay cita duplicada
        self.appointment_repo.find_by_doctor_patient_datetime.return_value = None
        
        # Configurar que no hay cita a la misma hora
        self.appointment_repo.find_patient_appointments_at_same_time.return_value = []
        
        # Configurar que hay una cita el mismo día
        self.appointment_repo.find_by_patient_and_date.return_value = [same_day_appointment]
        
        # Verificar que se lanza la excepción correcta
        with pytest.raises(ValueError, match="You can only have one appointment per day"):
            self.use_case.execute(self.appointment_data)
