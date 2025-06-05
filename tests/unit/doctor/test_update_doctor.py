import pytest
from unittest.mock import create_autospec
from medical_system.usecases.doctor.update_doctor import UpdateDoctorUseCase
from medical_system.usecases.dtos.doctor_dto import UpdateDoctorDTO
from medical_system.domain.entities.doctor import Doctor
from medical_system.domain.value_objects.email import Email
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.ports.repositories.doctor_repository import DoctorRepository

class TestUpdateDoctorUseCase:
    
    @pytest.fixture
    def doctor_repo(self):
        return create_autospec(DoctorRepository, instance=True)
    
    @pytest.fixture
    def existing_doctor(self):
        doctor = Doctor(
            name="Dr. Ana López",
            email=Email("ana.lopez@example.com"),
            specialty="Cardiología"
        )
        doctor.id = 1
        return doctor
    
    @pytest.fixture
    def update_data(self):
        return UpdateDoctorDTO(
            name="Dra. Ana María López",
            email="anamaria.lopez@example.com",
            specialty="Cardiología Pediátrica"
        )
    
    @pytest.fixture
    def use_case(self, doctor_repo, existing_doctor):
        doctor_repo.find_by_id.return_value = existing_doctor
        doctor_repo.find_by_email.return_value = None
        doctor_repo.update.return_value = existing_doctor
        return UpdateDoctorUseCase(doctor_repo)
    
    def test_should_update_doctor_when_admin_and_valid_data(self, use_case, doctor_repo, update_data, existing_doctor):
        result = use_case.execute(1, update_data, is_admin=True)
        
        assert result.id == 1
        assert result.name == "Dra. Ana María López"
        assert result.email == "anamaria.lopez@example.com"
        assert result.specialty == "Cardiología Pediátrica"
        doctor_repo.update.assert_called_once()
    
    def test_should_raise_error_when_not_admin(self, use_case, update_data):
        with pytest.raises(UnauthorizedError, match="Only administrators can update doctor information"):
            use_case.execute(1, update_data, is_admin=False)
    
    def test_should_raise_error_when_doctor_not_found(self, use_case, doctor_repo, update_data):
        doctor_repo.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Doctor not found"):
            use_case.execute(1, update_data, is_admin=True)
    
    def test_should_raise_error_when_email_already_in_use(self, use_case, doctor_repo, update_data, existing_doctor):
        other_doctor = Doctor(
            name="Dr. Otro Doctor",
            email=Email("anamaria.lopez@example.com"),
            specialty="Pediatría"
        )
        other_doctor.id = 2
        doctor_repo.find_by_email.return_value = other_doctor
        
        with pytest.raises(ValueError, match="Email is already in use by another doctor"):
            use_case.execute(1, update_data, is_admin=True)
    
    def test_should_update_only_provided_fields(self, use_case, doctor_repo, existing_doctor):
        partial_data = UpdateDoctorDTO(
            specialty="Cardiología Pediátrica"
        )
        
        result = use_case.execute(1, partial_data, is_admin=True)
        
        assert result.specialty == "Cardiología Pediátrica"
        assert result.name == "Dr. Ana López"
        assert result.email == "ana.lopez@example.com"
        doctor_repo.update.assert_called_once()
