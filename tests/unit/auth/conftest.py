import pytest
from fastapi.testclient import TestClient
from medical_system.interfaces.api.main import app
from medical_system.domain.entities.user import User
from datetime import datetime

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        is_active=True,
        created_at=datetime.utcnow(),
        metadata={"roles": ["user"]}
    )

@pytest.fixture
def admin_user():
    return User(
        id=2,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        is_active=True,
        created_at=datetime.utcnow(),
        metadata={"roles": ["admin"]}
    )

@pytest.fixture
def valid_token(mock_user):
    from medical_system.domain.auth.service import AuthService
    from medical_system.infrastructure.container import get_user_repository
    
    auth_service = AuthService(get_user_repository())
    tokens = auth_service.create_tokens(mock_user)
    return tokens.access_token

@pytest.fixture
def admin_token(admin_user):
    from medical_system.domain.auth.service import AuthService
    from medical_system.infrastructure.container import get_user_repository
    
    auth_service = AuthService(get_user_repository())
    tokens = auth_service.create_tokens(admin_user)
    return tokens.access_token
