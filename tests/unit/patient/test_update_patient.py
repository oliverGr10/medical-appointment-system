from unittest.mock import create_autospec
import pytest
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.repositories.patient_repository import PatientRepository
from medical_system.usecases.dtos.patient_dto import UpdatePatientDTO
from medical_system.usecases.patient.update_patient import UpdatePatientUseCase

class TestUpdatePatientUseCase:
    
    @pytest.fixture
    def patient_repo(self):
        return create_autospec(PatientRepository, instance=True)
    
    @pytest.fixture
    def patient(self, sample_patient):
        sample_patient.id = 1
        return sample_patient
    
    @pytest.fixture
    def update_data(self, patient):
        return UpdatePatientDTO(
            id=patient.id,
            name="Juan Carlos Pérez",
            email="juan.carlos@example.com",
            birth_date=patient.birth_date.replace(month=5, day=15)
        )
    
    @pytest.fixture
    def use_case(self, patient_repo, patient):
        patient_repo.find_by_id.return_value = patient
        patient_repo.find_by_email.return_value = None
        patient_repo.update.return_value = patient
        return UpdatePatientUseCase(patient_repo)
    
    def test_should_update_patient_when_admin_and_data_valid(
        self, use_case, patient_repo, update_data, patient
    ):
        result = use_case.execute(update_data, is_admin=True)
        
        assert result.id == 1
        assert result.name == "Juan Carlos Pérez"
        assert result.email == "juan.carlos@example.com"
        assert result.birth_date == date(1990, 5, 15)
        patient_repo.update.assert_called_once()
    
    def test_should_raise_error_when_not_admin(self, use_case, update_data):
        with pytest.raises(UnauthorizedError, match="Only administrators can update patient information"):
            use_case.execute(update_data, is_admin=False)
    
    def test_should_raise_error_when_patient_not_found(self, use_case, patient_repo, update_data):
        patient_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Patient not found"):
            use_case.execute(update_data, is_admin=True)
    
    def test_should_raise_error_when_email_already_in_use(
        self, use_case, patient_repo, update_data, patient, sample_patient
    ):
        other_patient = sample_patient
        other_patient.id = 2
        other_patient.email = update_data.email
        patient_repo.find_by_email.return_value = other_patient
        
        with pytest.raises(ValueError, match="Email is already in use by another patient"):
            use_case.execute(update_data, is_admin=True)
    
    def test_should_update_only_provided_fields(
        self, use_case, patient_repo, patient
    ):
        partial_data = UpdatePatientDTO(
            id=1,
            name="Juan Carlos Pérez"
        )
        
        result = use_case.execute(partial_data, is_admin=True)
        
        assert result.id == patient.id
        assert result.name == "Juan Carlos Pérez"
        assert result.email == patient.email
        assert result.birth_date == patient.birth_date
        patient_repo.update.assert_called_once()
