from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt

from medical_system.domain.entities.user import User
from medical_system.domain.ports.repositories.user_repository import UserRepository
from medical_system.domain.auth.config import (
    verify_password,
    get_password_hash,
    get_token_expires_delta,
    get_refresh_token_expires_delta,
    UserRole,
    SECRET_KEY,
    ALGORITHM
)
from medical_system.domain.auth.schemas import Token, TokenData, UserCreate
from medical_system.domain.exceptions import (
    UnauthorizedError,
    BadRequestError,
    NotFoundError
)

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, email: str, password: str) -> User:
        try:
            user = self.user_repository.find_by_email(email.lower())
            if not user:
                raise UnauthorizedError("Credenciales inválidas")
            if not hasattr(user, 'password_hash') or not user.password_hash:
                raise UnauthorizedError("Credenciales inválidas")
                
            password_valid = verify_password(password, user.password_hash)
 
            if not password_valid:
                raise UnauthorizedError("Credenciales inválidas")
                
            if not getattr(user, 'is_active', True):
                raise UnauthorizedError("Usuario inactivo")
            return user
            
        except UnauthorizedError:
            raise
        except Exception as e:
            raise UnauthorizedError("Error durante la autenticación")

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        try:
            to_encode = data.copy()
            
            delta = expires_delta if expires_delta is not None else get_token_expires_delta()
            
            expire = datetime.now(datetime.timezone.utc) + delta
        
            to_encode.update({"exp": expire})

            token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

            
            return token
            
        except JWTError as je:
            raise UnauthorizedError(f"Error JWT al generar el token: {str(je)}")
        except Exception as e:
            raise UnauthorizedError("Error inesperado al generar el token de acceso")

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = get_refresh_token_expires_delta()

        if "user_id" not in to_encode:
            raise ValueError("El payload debe contener user_id")
        if "sub" not in to_encode:
            raise ValueError("El payload debe contener sub (email)")
            
        to_encode.update({
            "exp": expire, 
            "type": "refresh",
            "user_id": to_encode["user_id"],
            "sub": to_encode["sub"]
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_tokens(self, user: User) -> Token:

        if not user or not hasattr(user, 'id') or not hasattr(user, 'email'):
            raise ValueError("Usuario inválido")
            
        user_roles = user.metadata.get("roles", []) if hasattr(user, 'metadata') else []
        
        try:
            expires_at = get_token_expires_delta()
            
            now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.utcnow()
            
            if expires_at <= now:
                raise ValueError("La fecha de expiración es anterior a la hora actual")
                
            expires_delta = expires_at - now
            
            access_token = self.create_access_token(
                data={
                    "sub": user.email,
                    "user_id": user.id,
                    "roles": user_roles,
                    "type": "access"
                },
                expires_delta=expires_delta
            )
            
            refresh_token = self.create_refresh_token(
                data={
                    "sub": user.email,
                    "user_id": user.id
                }
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_at=expires_at,
                refresh_token=refresh_token
            )
            
        except Exception as e:
            raise UnauthorizedError("Error al generar los tokens") from e
    
    def verify_token(self, token: str, token_type: Optional[str] = None) -> TokenData:
        credentials_exception = UnauthorizedError("Token inválido o expirado")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            if token_type is not None:
                if payload.get("type") != token_type:
                    raise UnauthorizedError(f"Tipo de token inválido. Se esperaba: {token_type}")

            email: str = payload.get("sub")
            if not email:
                raise credentials_exception
                
            user_id: int = payload.get("user_id")
            if user_id is None:
                raise credentials_exception
                
            roles: List[str] = payload.get("roles", [])
            
            return TokenData(email=email, user_id=user_id, roles=roles)
            
        except JWTError as e:
            raise UnauthorizedError(f"Error de autenticación: {str(e)}")

    def get_current_user(self, token: str) -> User:
        token_data = self.verify_token(token)
        user = self.user_repository.find_by_id(token_data.user_id)
        if user is None:
            raise UnauthorizedError("Usuario no encontrado")
        return user

    def has_required_roles(self, token: str, required_roles: List[str]) -> bool:
        if not required_roles:
            return True
            
        token_data = self.verify_token(token)
        user_roles = set(token_data.roles)
        return any(role in user_roles for role in required_roles)

    def create_user(self, user_data: UserCreate) -> User:
        if self.user_repository.find_by_email(user_data.email):
            raise BadRequestError("El correo electrónico ya está registrado")
        
        user_dict = user_data.dict(exclude={"password", "password_confirm"})
        user_dict["password_hash"] = get_password_hash(user_data.password)

        if "metadata" not in user_dict:
            user_dict["metadata"] = {}
        
        if "roles" not in user_dict["metadata"]:
            user_dict["metadata"]["roles"] = [UserRole.PATIENT]
        
        user = User(**user_dict)
        return self.user_repository.save(user)

    def update_user_roles(self, user_id: int, roles: List[str]) -> User:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")
        
        valid_roles = [role for role in dir(UserRole) if not role.startswith('_')]
        for role in roles:
            if role not in valid_roles:
                raise BadRequestError(f"Rol no válido: {role}")
        
        if not hasattr(user, 'metadata') or not user.metadata:
            user.metadata = {}
        
        user.metadata["roles"] = roles
        return self.user_repository.save(user)
