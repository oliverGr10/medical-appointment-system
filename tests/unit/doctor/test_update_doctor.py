import pytest
from unittest.mock import MagicMock
from medical_system.application.use_cases.doctor.update_doctor import UpdateDoctorUseCase
from medical_system.application.dtos.doctor_dto import UpdateDoctorDTO
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError

class TestUpdateDoctorUseCase:
    """Pruebas para el caso de uso de actualización de doctor."""

    @pytest.fixture
    def setup(self):
        # Configuración común para las pruebas
        self.doctor_repo = MagicMock()
        self.use_case = UpdateDoctorUseCase(self.doctor_repo)
        
        # Doctor de prueba
        self.doctor = Doctor(
            name="Dr. Ana López",
            email=Email("ana.lopez@example.com"),
            specialty="Cardiología"
        )
        self.doctor.id = 1
        
        # Datos de actualización
        self.update_data = UpdateDoctorDTO(
            id=1,
            name="Dra. Ana María López",
            email="anamaria.lopez@example.com",
            specialty="Cardiología Pediátrica"
        )
        
        # Configurar el repositorio
        self.doctor_repo.find_by_id.return_value = self.doctor
        self.doctor_repo.find_by_email.return_value = None
        self.doctor_repo.update.return_value = self.doctor
        
        return self
    
    def test_update_doctor_success(self, setup):
        """Prueba la actualización exitosa de un doctor."""
        # Ejecutar
        result = self.use_case.execute(self.update_data, is_admin=True)
        
        # Verificar
        assert result.id == 1
        assert result.name == "Dra. Ana María López"
        assert result.email == "anamaria.lopez@example.com"
        assert result.specialty == "Cardiología Pediátrica"
        self.doctor_repo.update.assert_called_once()
    
    def test_update_doctor_unauthorized(self, setup):
        """Prueba que solo los administradores puedan actualizar doctores."""
        with pytest.raises(UnauthorizedError, match="Only administrators can update doctor information"):
            self.use_case.execute(self.update_data, is_admin=False)
    
    def test_update_doctor_not_found(self, setup):
        """Prueba cuando el doctor no existe."""
        self.doctor_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Doctor not found"):
            self.use_case.execute(self.update_data, is_admin=True)
    
    def test_update_doctor_duplicate_email(self, setup):
        """Prueba cuando el correo electrónico ya está en uso."""
        # Configurar otro doctor con el mismo correo
        other_doctor = Doctor(
            name="Dr. Otro Doctor",
            email=Email("anamaria.lopez@example.com"),
            specialty="Pediatría"
        )
        other_doctor.id = 2
        self.doctor_repo.find_by_email.return_value = other_doctor
        
        with pytest.raises(ValueError, match="Email is already in use by another doctor"):
            self.use_case.execute(self.update_data, is_admin=True)
    
    def test_update_partial_data(self, setup):
        """Prueba actualizar solo algunos campos del doctor."""
        # Datos de actualización parcial
        partial_data = UpdateDoctorDTO(
            id=1,
            specialty="Cardiología Pediátrica"
            # name y email no se incluyen
        )
        
        # Ejecutar
        result = self.use_case.execute(partial_data, is_admin=True)
        
        # Verificar
        assert result.id == 1
        assert result.name == "Dr. Ana López"  # Sin cambios
        assert result.email == "ana.lopez@example.com"  # Sin cambios
        assert result.specialty == "Cardiología Pediátrica"  # Actualizado
        self.doctor_repo.update.assert_called_once()
