from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import Optional, List
from medical_system.domain.auth.service import AuthService
from medical_system.domain.auth.schemas import TokenData
from medical_system.domain.entities.user import User
from medical_system.domain.ports.repositories.user_repository import UserRepository
from medical_system.domain.exceptions import UnauthorizedError

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, required_roles: Optional[List[str]] = None):
        super().__init__(auto_error=auto_error)
        self.required_roles = required_roles or []

    def __call__(self, request: Request) -> TokenData:
        if request.method == "OPTIONS":
            return TokenData(sub="preflight", scopes=[])
            
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                print("[AUTH] No se proporcionó el encabezado de autorización")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No se proporcionaron credenciales de autenticación",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            parts = auth_header.split()

            if len(parts) == 2:
                if parts[0].lower() != "bearer":
                    print(f"[AUTH] Formato de token inválido: {auth_header}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Formato de token inválido. Use: Bearer <token> o solo el token",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                token = parts[1].strip()
            elif len(parts) == 1:
                token = parts[0].strip()
            else:
                print(f"[AUTH] Formato de token inválido: {auth_header}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Formato de token inválido. Use: Bearer <token> o solo el token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            if not token:
                print("[AUTH] Token vacío")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token no proporcionado",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            if not token or not token.strip():
                print("[AUTH] Token vacío")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token no proporcionado o vacío",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            if len(token.split('.')) != 3:
                print("[AUTH] Formato de token JWT inválido")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Formato de token JWT inválido",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            auth_service: Optional[AuthService] = getattr(request.app.state, 'auth_service', None)
            if not auth_service:
                print("[AUTH] Servicio de autenticación no disponible")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor: servicio de autenticación no configurado"
                )
            
            try:
                print(f"[AUTH] Verificando token: {token[:10]}...")
                token_data = auth_service.verify_token(token)
                
                if not token_data:
                    print("[AUTH] Token inválido o expirado")
                    raise UnauthorizedError("Token inválido o expirado")
                
                print(f"[AUTH] Token verificado para usuario: {getattr(token_data, 'sub', 'unknown')}")

                if self.required_roles:
                    user_roles = set(getattr(token_data, 'roles', []) or [])
                    if not any(role in user_roles for role in self.required_roles):
                        print(f"[AUTH] Permisos insuficientes. Roles requeridos: {self.required_roles}, roles del usuario: {user_roles}")
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tiene permisos suficientes para acceder a este recurso"
                        )

                request.state.user = token_data
                return token_data
                
            except UnauthorizedError as e:
                print(f"[AUTH] Error de autenticación: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e) or "Token inválido o expirado",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
        except HTTPException:
            raise
            
        except Exception as e:
            print(f"[AUTH] Error inesperado en el middleware de autenticación: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al procesar la autenticación"
            )

class AuthDependency:
    def __init__(self, required_roles: Optional[List[str]] = None):
        self.required_roles = required_roles or []
    
    async def __call__(self, request: Request) -> User:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Se requiere autenticación con token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            if not auth_header or not auth_header.strip():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No se proporcionó el token de autenticación",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            parts = auth_header.split()
            if len(parts) == 2:
                scheme, token = parts
                if scheme.lower() != 'bearer':
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Esquema de autenticación inválido. Use: 'Bearer <token>'",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            elif len(parts) == 1:
                token = parts[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Formato de token inválido. Use: 'Bearer <token>' o solo el token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not token or not token.strip():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No se proporcionó un token de autenticación válido",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            token_parts = token.split('.')
            if len(token_parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Formato de token JWT inválido: el token debe tener tres partes separadas por puntos",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            auth_service: AuthService = getattr(request.app.state, 'auth_service', None)
            if not auth_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error de configuración del servidor de autenticación",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            try:
                token_data = auth_service.verify_token(token)

                user_repository: UserRepository = getattr(request.app.state, 'user_repository', None)
                if not user_repository:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error de configuración del repositorio de usuarios",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                user = user_repository.find_by_id(token_data.user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Usuario no encontrado",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                if self.required_roles:
                    user_roles = set(getattr(user, 'metadata', {}).get("roles", []))
                    if not any(role in user_roles for role in self.required_roles):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tiene permisos suficientes para acceder a este recurso",
                            headers={"WWW-Authenticate": "Bearer"}
                        )
                
                return user
                
            except UnauthorizedError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e) if str(e) else "Token inválido o expirado",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
        except HTTPException as http_exc:
            raise http_exc
            
        except Exception as e:
            import traceback
            error_msg = f"Error inesperado en la autenticación: {str(e)}"
            print(f"[AUTH] {error_msg}")
            print(f"[AUTH] Traceback: {traceback.format_exc()}")

            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Error interno del servidor al procesar la autenticación"
            
            import os
            if os.getenv("ENV") == "development":
                detail = f"{detail}: {str(e)}"
            
            raise HTTPException(
                status_code=status_code,
                detail=detail,
                headers={"WWW-Authenticate": "Bearer"} if status_code == 401 else {}
            )

async def get_current_user(request: Request) -> User:
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se proporcionó el token de autenticación",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Formato de token inválido. Use: 'Bearer <token>' o solo el token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        auth_service: AuthService = request.app.state.auth_service
        user_repository: UserRepository = request.app.state.user_repository
        
        try:
            token_data = auth_service.verify_token(token)
            user = user_repository.find_by_id(token_data.user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
                
            return user
            
        except UnauthorizedError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException as he:
        print(f"[AUTH] Error de autenticación: {str(he.detail)}")
        raise he
    except Exception as e:
        print(f"[AUTH] Error inesperado en get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

def require_roles(required_roles: List[str]):

    def decorator(current_user: User = Depends(get_current_active_user)):
        user_roles = set(current_user.metadata.get("roles", []))
        if not any(role in user_roles for role in required_roles):
            _raise_403()
        return current_user
    return decorator

def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:

    return current_user if current_user.is_admin or current_user.has_role("admin") else _raise_403()

def get_doctor_user(current_user: User = Depends(get_current_active_user)) -> User:

    return current_user if current_user.has_role("doctor") else _raise_403()

def get_patient_user(current_user: User = Depends(get_current_active_user)) -> User:

    return current_user if current_user.has_role("patient") else _raise_403()

def get_doctor_or_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.has_role("doctor") or current_user.has_role("admin") or current_user.is_admin:
        return current_user
    _raise_403()

def _raise_403():
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos suficientes para acceder a este recurso")
