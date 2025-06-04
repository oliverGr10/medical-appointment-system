"""
Pruebas unitarias para el caso de uso CreatePatientUseCase.
"""
import pytest
from unittest.mock import MagicMock
from datetime import date
from medical_system.application.use_cases.patient.create_patient import CreatePatientUseCase
from medical_system.application.dtos.patient_dto import CreatePatientDTO, PatientDTO
from medical_system.domain.entities.patient import Patient
from medical_system.domain.value_objects.email import Email

class TestCreatePatientUseCase:
    """Pruebas para el caso de uso de creación de pacientes."""
    
    def test_create_patient_success(self):
        # Configurar mocks
        mock_repo = MagicMock()
        mock_repo.find_by_email.return_value = None
        
        # Crear un paciente de prueba
        test_patient = Patient(
            name="Juan Pérez",
            email=Email("juan@example.com"),
            birth_date=date(1990, 1, 1)
        )
        test_patient.id = 1  # Asignar ID después de la creación
        mock_repo.save.return_value = test_patient
        
        # Crear caso de uso
        use_case = CreatePatientUseCase(mock_repo)
        
        # Ejecutar
        result = use_case.execute(CreatePatientDTO(
            name="Juan Pérez",
            email="juan@example.com",
            birth_date=date(1990, 1, 1)
        ))
        
        # Verificar
        assert isinstance(result, PatientDTO)
        assert result.id == 1
        assert result.name == "Juan Pérez"
        assert result.email == "juan@example.com"
        mock_repo.save.assert_called_once()
    
    def test_create_patient_duplicate_email(self):
        # Configurar mocks
        mock_repo = MagicMock()
        
        # Crear un paciente existente
        existing_patient = Patient(
            name="Juan Pérez",
            email=Email("juan@example.com"),
            birth_date=date(1990, 1, 1)
        )
        existing_patient.id = 1
        mock_repo.find_by_email.return_value = existing_patient
        
        # Crear caso de uso
        use_case = CreatePatientUseCase(mock_repo)
        
        # Verificar que lanza excepción
        with pytest.raises(ValueError, match="A patient with this email already exists"):
            use_case.execute(CreatePatientDTO(
                name="Otro Nombre",
                email="juan@example.com",
                birth_date=date(1995, 1, 1)
            ))
