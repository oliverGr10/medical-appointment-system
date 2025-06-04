"""
Pruebas unitarias para el caso de uso ListDoctorsBySpecialtyUseCase.
"""
import pytest
from unittest.mock import MagicMock
from medical_system.application.use_cases.doctor.list_doctors_by_specialty import ListDoctorsBySpecialtyUseCase
from medical_system.application.dtos.doctor_dto import DoctorDTO
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email

class TestListDoctorsBySpecialtyUseCase:
    """Pruebas para el caso de uso de listar doctores por especialidad."""
    
    def test_list_doctors_by_specialty(self):
        # Configurar mocks
        mock_repo = MagicMock()
        
        # Crear doctores de prueba
        doctor1 = Doctor(
            name="Dr. Carlos García",
            email=Email("dr.garcia@example.com"),
            specialty="Cardiología"
        )
        doctor1.id = 1
        
        doctor2 = Doctor(
            name="Dra. Ana López",
            email=Email("dra.lopez@example.com"),
            specialty="Cardiología"
        )
        doctor2.id = 2
        
        mock_repo.find_by_specialty.return_value = [doctor1, doctor2]
        
        # Crear caso de uso
        use_case = ListDoctorsBySpecialtyUseCase(mock_repo)
        
        # Ejecutar
        result = use_case.execute("Cardiología")
        
        # Verificar
        assert len(result) == 2
        assert all(isinstance(d, DoctorDTO) for d in result)
        assert result[0].specialty == "Cardiología"
        assert result[1].specialty == "Cardiología"
        mock_repo.find_by_specialty.assert_called_once_with("Cardiología")
