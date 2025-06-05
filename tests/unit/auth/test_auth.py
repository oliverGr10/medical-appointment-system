import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from medical_system.domain.entities.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TestAuthEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self):

        self.app = FastAPI()

        self.valid_token = "test.valid.token"
        self.valid_access_token = "test.valid.access.token"
        self.valid_refresh_token = "test.valid.refresh.token"

        self.test_user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            metadata={"roles": ["user"]}
        )
        
        self.mock_user_repo = MagicMock()
        self.mock_user_repo.get_user_by_email.return_value = self.test_user

        self.valid_tokens = {
            "access_token": self.valid_access_token,
            "refresh_token": self.valid_refresh_token,
            "token_type": "bearer"
        }

        self.mock_auth_service = MagicMock()
        self.mock_auth_service.authenticate_user.return_value = self.test_user
        self.mock_auth_service.create_tokens.return_value = self.valid_tokens

        self.mock_user_repo = MagicMock()
        self.mock_user_repo.get_user_by_email.return_value = self.test_user

        self.app = FastAPI()

        def get_auth_service_mock():
            return self.mock_auth_service
            
        def get_user_repo_mock():
            return self.mock_user_repo
   
        async def get_current_user_mock(token: str = Depends(oauth2_scheme)):
            if token != self.valid_access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return self.test_user

        self.app.dependency_overrides["get_auth_service"] = get_auth_service_mock
        self.app.dependency_overrides["get_user_repository"] = get_user_repo_mock

        @self.app.post("/api/auth/login")
        async def login(login_data: dict):
            user = self.mock_auth_service.authenticate_user(
                email=login_data.get("email"), 
                password=login_data.get("password")
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return self.mock_auth_service.create_tokens(user.id, user.email)
            
        @self.app.get("/api/auth/me")
        async def read_users_me(current_user: User = Depends(get_current_user_mock)):
            return current_user

        self.client = TestClient(self.app)
    
    def test_login_successful(self):
        self.mock_auth_service.authenticate_user.return_value = self.test_user

        login_data = {
            "email": "test@example.com",
            "password": "testpass"
        }

        response = self.client.post(
            "/api/auth/login",
            json=login_data
        )

        assert response.status_code == 200, f"Error inesperado: {response.json()}"
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
    
    def test_login_invalid_credentials(self):

        self.mock_auth_service.authenticate_user.return_value = None

        invalid_login_data = {
            "email": "wrong@example.com",
            "password": "wrongpass"
        }

        response = self.client.post(
            "/api/auth/login",
            json=invalid_login_data
        )

        assert response.status_code == 401, f"Error inesperado: {response.json()}"
        assert response.json()["detail"] == "Incorrect email or password"
    
    def test_get_current_user_successful(self):

        headers = {"Authorization": f"Bearer {self.valid_access_token}"}

        self.mock_auth_service.get_current_user.return_value = self.test_user

        response = self.client.get(
            "/api/auth/me",
            headers=headers
        )

        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self):

        response = self.client.get("/api/auth/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
