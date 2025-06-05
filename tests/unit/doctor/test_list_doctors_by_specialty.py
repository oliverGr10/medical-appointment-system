import pytest
from unittest.mock import MagicMock, create_autospec
from medical_system.usecases.doctor.list_doctors_by_specialty import ListDoctorsBySpecialtyUseCase
from medical_system.usecases.dtos.doctor_dto import DoctorDTO
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.repositories.doctor_repository import DoctorRepository

class TestListDoctorsBySpecialtyUseCase:
    
    @pytest.fixture
    def mock_repo(self):
        return create_autospec(DoctorRepository, instance=True)
    
    @pytest.fixture
    def sample_doctors(self):
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
        
        return [doctor1, doctor2]
    
    def test_should_return_doctors_when_specialty_exists(self, mock_repo, sample_doctors):
        mock_repo.find_by_specialty.return_value = sample_doctors
        use_case = ListDoctorsBySpecialtyUseCase(mock_repo)
        
        result = use_case.execute("Cardiología")
        
        assert len(result) == 2
        assert isinstance(result[0], DoctorDTO)
        assert result[0].name == "Dr. Carlos García"
        assert result[1].email == "dra.lopez@example.com"
        mock_repo.find_by_specialty.assert_called_once_with("Cardiología")
    
    def test_should_return_empty_list_when_no_doctors_found(self, mock_repo):
        mock_repo.find_by_specialty.return_value = []
        use_case = ListDoctorsBySpecialtyUseCase(mock_repo)
        
        result = use_case.execute("Neurología")
        
        assert result == []
        mock_repo.find_by_specialty.assert_called_once_with("Neurología")
    
    def test_should_handle_empty_specialty(self, mock_repo):
        mock_repo.find_by_specialty.return_value = []
        use_case = ListDoctorsBySpecialtyUseCase(mock_repo)
        
        result = use_case.execute("")
        
        assert result == []
        mock_repo.find_by_specialty.assert_called_once_with("")
