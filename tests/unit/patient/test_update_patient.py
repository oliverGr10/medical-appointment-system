import pytest
from unittest.mock import MagicMock
from datetime import date
from medical_system.application.use_cases.patient.update_patient import UpdatePatientUseCase
from medical_system.application.dtos.patient_dto import UpdatePatientDTO, PatientDTO
from medical_system.domain.entities.patient import Patient
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestUpdatePatientUseCase:
    """Pruebas para el caso de uso de actualización de paciente."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.patient_repo = MagicMock()
        self.use_case = UpdatePatientUseCase(self.patient_repo)
        
        # Paciente de prueba
        self.patient = Patient(
            name="Juan Pérez",
            email=Email("juan@example.com"),
            birth_date=date(1990, 1, 1)
        )
        self.patient.id = 1
        
        # Datos de actualización
        self.update_data = UpdatePatientDTO(
            id=1,
            name="Juan Carlos Pérez",
            email="juan.carlos@example.com",
            birth_date=date(1990, 5, 15)
        )
        
        # Configurar el repositorio
        self.patient_repo.find_by_id.return_value = self.patient
        self.patient_repo.find_by_email.return_value = None
        self.patient_repo.update.return_value = self.patient
        
        return self
    
    def test_update_patient_success(self, setup):
        """Prueba la actualización exitosa de un paciente."""
        # Ejecutar
        result = self.use_case.execute(self.update_data, is_admin=True)
        
        # Verificar
        assert result.id == 1
        assert result.name == "Juan Carlos Pérez"
        assert result.email == "juan.carlos@example.com"
        assert result.birth_date == date(1990, 5, 15)
        self.patient_repo.update.assert_called_once()
    
    def test_update_patient_unauthorized(self, setup):
        """Prueba que solo los administradores puedan actualizar pacientes."""
        with pytest.raises(UnauthorizedError, match="Only administrators can update patient information"):
            self.use_case.execute(self.update_data, is_admin=False)
    
    def test_update_patient_not_found(self, setup):
        """Prueba cuando el paciente no existe."""
        self.patient_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Patient not found"):
            self.use_case.execute(self.update_data, is_admin=True)
    
    def test_update_patient_duplicate_email(self, setup):
        """Prueba cuando el correo electrónico ya está en uso."""
        # Configurar otro paciente con el mismo correo
        other_patient = Patient(
            name="Otro Paciente",
            email=Email("juan.carlos@example.com"),
            birth_date=date(1985, 1, 1)
        )
        other_patient.id = 2
        self.patient_repo.find_by_email.return_value = other_patient
        
        with pytest.raises(ValueError, match="Email is already in use by another patient"):
            self.use_case.execute(self.update_data, is_admin=True)
    
    def test_update_partial_data(self, setup):
        """Prueba actualizar solo algunos campos del paciente."""
        # Datos de actualización parcial
        partial_data = UpdatePatientDTO(
            id=1,
            name="Juan Carlos Pérez"
            # email y birth_date no se incluyen
        )
        
        # Ejecutar
        result = self.use_case.execute(partial_data, is_admin=True)
        
        # Verificar
        assert result.id == 1
        assert result.name == "Juan Carlos Pérez"  # Actualizado
        assert result.email == "juan@example.com"  # Sin cambios
        assert result.birth_date == date(1990, 1, 1)  # Sin cambios
        self.patient_repo.update.assert_called_once()
