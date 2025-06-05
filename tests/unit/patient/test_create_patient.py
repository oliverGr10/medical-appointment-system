from unittest.mock import create_autospec
import pytest
from medical_system.domain.ports.repositories.patient_repository import PatientRepository
from medical_system.usecases.dtos.patient_dto import CreatePatientDTO, PatientDTO
from medical_system.usecases.patient.create_patient import CreatePatientUseCase

class TestCreatePatientUseCase:
    
    @pytest.fixture
    def patient_repo(self):
        return create_autospec(PatientRepository, instance=True)
    
    @pytest.fixture
    def patient_data(self, sample_patient):
        return {
            "name": sample_patient.name,
            "email": str(sample_patient.email),
            "birth_date": sample_patient.birth_date
        }
    
    @pytest.fixture
    def use_case(self, patient_repo):
        return CreatePatientUseCase(patient_repo)
    
    def test_should_create_patient_when_email_not_exists(
        self, use_case, patient_repo, patient_data, sample_patient
    ):
        patient_repo.find_by_email.return_value = None
        sample_patient.id = 1
        patient_repo.save.return_value = sample_patient
        
        result = use_case.execute(CreatePatientDTO(**patient_data))
        
        assert isinstance(result, PatientDTO)
        assert result.id == 1
        assert result.name == patient_data["name"]
        assert result.email == patient_data["email"]
        patient_repo.find_by_email.assert_called_once_with(patient_data["email"])
        patient_repo.save.assert_called_once()
    
    def test_should_raise_error_when_email_already_exists(
        self, use_case, patient_repo, patient_data, sample_patient
    ):
        sample_patient.id = 1
        patient_repo.find_by_email.return_value = sample_patient
        
        with pytest.raises(ValueError, match="A patient with this email already exists"):
            use_case.execute(CreatePatientDTO(**patient_data))
        
        patient_repo.find_by_email.assert_called_once_with(patient_data["email"])
        patient_repo.save.assert_not_called()
    
    def test_should_raise_error_when_invalid_email_format(self, use_case, patient_data, patient_repo):
        patient_repo.find_by_email.return_value = None
        with pytest.raises(ValueError, match="Invalid email format"):
            use_case.execute(CreatePatientDTO(
                name=patient_data["name"],
                email="invalid-email",
                birth_date=patient_data["birth_date"]
            ))
        patient_repo.find_by_email.assert_called_once_with("invalid-email")
