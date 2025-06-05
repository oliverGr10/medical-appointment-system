from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Any, List
from medical_system.domain.entities.user import User
from medical_system.domain.ports.repositories.user_repository import UserRepository
from medical_system.domain.auth.service import AuthService
from medical_system.domain.exceptions import UnauthorizedError
from medical_system.domain.auth.schemas import (
    UserCreate, 
    UserResponse, 
    Token,
    UserUpdate,
    UserRoleUpdate
)
from medical_system.interfaces.api.middleware.auth_middleware import (
    get_current_user,
    get_admin_user
)
from medical_system.infrastructure.container import get_user_repository

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        401: {"description": "No autorizado - Token inválido o expirado"},
        403: {"description": "Operación no permitida - Permisos insuficientes"},
        422: {"description": "Error de validación en los datos de entrada"}
    },
    dependencies=[]
)

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description=(
        "## Autenticación de usuario\n\n"
        "Este endpoint permite a los usuarios autenticarse en el sistema utilizando su email y contraseña. "
        "Al autenticarse correctamente, se devuelve un token JWT que debe ser incluido en el encabezado "
        "`Authorization` de las peticiones a los endpoints protegidos.\n\n"
        "### Pasos para usar el token:\n"
        "1. Realice una petición POST a este endpoint con email y contraseña\n"
        "2. Copie el valor del campo `access_token` de la respuesta\n"
        "3. En Swagger UI, haga clic en el botón **Authorize** (🔒) en la esquina superior derecha\n"
        "4. Ingrese: `Bearer <su_token>` (reemplace `<su_token>` con el token copiado)"
    ),
    response_description="Token de acceso JWT",
    responses={
        200: {
            "description": "Autenticación exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_at": "2023-01-01T12:00:00.000Z",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        400: {"description": "Credenciales inválidas o formato incorrecto"},
        401: {"description": "No autorizado - Credenciales incorrectas"},
        403: {"description": "Cuenta inactiva o sin permisos suficientes"}
    }
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:

    print(f"[LOGIN] Intento de inicio de sesión para: {login_data.email}")
    
    try:

        print(f"[LOGIN] Autenticando usuario: {login_data.email}")
        
        if "@" not in login_data.email:
            print(f"[LOGIN] Formato de email inválido: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de correo electrónico inválido"
            )
        
        if not login_data.password:
            print("[LOGIN] No se proporcionó contraseña")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña es requerida"
            )
        
        try:
            user = auth_service.authenticate_user(login_data.email.lower().strip(), login_data.password)
            
            if not user:
                print(f"[LOGIN] Usuario no encontrado o contraseña incorrecta: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales inválidas",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            print(f"[LOGIN] Autenticación exitosa para: {user.email}")
            
        except HTTPException as http_exc:
            raise http_exc
        except UnauthorizedError as e:
            print(f"[LOGIN] Error de autenticación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            print(f"[LOGIN] Error inesperado durante la autenticación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor durante la autenticación"
            )

        if not getattr(user, 'is_active', True):
            print(f"[LOGIN] Usuario inactivo: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta inactiva. Por favor, contacte al administrador."
            )
        
        try:
            print(f"[LOGIN] Generando tokens para: {user.email}")
            tokens = auth_service.create_tokens(user)
            
            if not tokens or not tokens.access_token:
                raise Exception("No se pudo generar el token de acceso")
                
            print(f"[LOGIN] Tokens generados exitosamente para: {user.email}")

            token_type = getattr(tokens, 'token_type', 'bearer').lower()

            response_data = {
                "access_token": tokens.access_token,
                "token_type": token_type,
                "expires_in": (tokens.expires_at - datetime.now()).total_seconds() if hasattr(tokens, 'expires_at') else 3600,
                "expires_at": tokens.expires_at.isoformat() if hasattr(tokens, 'expires_at') else None,
                "refresh_token": getattr(tokens, 'refresh_token', None)
            }

            response_data = {k: v for k, v in response_data.items() if v is not None}
            return response_data
            
        except Exception as token_error:
            print(f"[LOGIN] Error al generar tokens: {str(token_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar los tokens de autenticación"
            )
        
    except HTTPException as he:

        print(f"[LOGIN] Error de autenticación: {str(he.detail)}")
        raise
        
    except Exception as e:
        error_msg = f"Error inesperado durante el inicio de sesión: {str(e)}"
        print(f"[LOGIN] {error_msg}")
        print(f"[LOGIN] Tipo de excepción: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la autenticación"
        )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    try:
        user = auth_service.create_user(user_in)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Obtener información del usuario actual",
    description="Devuelve la información del usuario autenticado actualmente",
    response_description="Datos del usuario autenticado",
    responses={
        200: {"description": "Información del usuario obtenida correctamente"},
        401: {"description": "No autenticado - Se requiere token de acceso"},
        404: {"description": "Usuario no encontrado"}
    }
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'is_active': current_user.is_active,
            'is_admin': getattr(current_user, 'is_admin', False),
            'created_at': current_user.created_at,
            'updated_at': getattr(current_user, 'updated_at', None),
            'last_login': getattr(current_user, 'last_login', None),
            'metadata': getattr(current_user, 'metadata', {})
        }
        
        return UserResponse(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en /me: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el usuario: {str(e)}"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    try:
        update_data = user_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)

        user_repository = auth_service.user_repository
        updated_user = user_repository.save(current_user)
        return updated_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/refresh", 
    response_model=Token,
    operation_id="refresh_token",
    summary="Actualizar token de acceso",
    description="Obtiene un nuevo token de acceso utilizando un token de actualización"
)
@router.put(
    "/refresh", 
    response_model=Token,
    operation_id="refresh_token_put",
    include_in_schema=False
)
async def refresh_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    print("Iniciando proceso de refresh token...")
    
    auth_header = request.headers.get("Authorization")
    print(f"Authorization header: {auth_header}")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        print("Error: No se proporcionó token o no tiene el formato correcto")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token de actualización en el formato 'Bearer <token>'"
        )
    
    try:
        refresh_token = auth_header.split(" ")[1]
        print("Token de actualización extraído correctamente")
        
        print("Verificando token...")
        try:

            token_data = auth_service.verify_token(refresh_token, token_type="refresh")
            print(f"Token verificado. User ID: {token_data.user_id}")
            
            print(f"Buscando usuario con ID: {token_data.user_id}")
            user = auth_service.user_repository.find_by_id(token_data.user_id)
            if not user:
                print(f"Usuario con ID {token_data.user_id} no encontrado")
                raise UnauthorizedError("Usuario no encontrado")
                
            if not getattr(user, 'is_active', True):
                print(f"Usuario {getattr(user, 'email', 'unknown')} está inactivo")
                raise UnauthorizedError("Usuario inactivo")
                
            print("Generando nuevos tokens...")
            tokens = auth_service.create_tokens(user)
            print("Tokens generados exitosamente")
            return tokens
            
        except UnauthorizedError as e:
            print(f"Error de autorización: {str(e)}")
            raise
        except Exception as e:
            print(f"Error al verificar el token: {str(e)}")
            raise UnauthorizedError(f"Token inválido: {str(e)}")
            
    except HTTPException:
        raise
    except UnauthorizedError as e:
        print(f"Error de autorización: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Error inesperado en refresh_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la solicitud de actualización de token"
        )

@router.put("/users/{user_id}/roles", response_model=UserResponse, dependencies=[Depends(get_admin_user)])
async def update_user_roles(
    user_id: int,
    roles_in: UserRoleUpdate,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:

    try:
        updated_user = auth_service.update_user_roles(user_id, roles_in.roles)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(get_admin_user)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    users = auth_service.user_repository.list_all()[skip:skip + limit]
    return users

@router.get(
    "/verify-token", 
    response_model=UserResponse, 
    summary="Verifica si un token JWT es válido",
    responses={
        200: {"description": "Token válido, devuelve información del usuario"},
        401: {"description": "Token inválido o expirado"}
    }
)
async def verify_token(current_user: User = Depends(get_current_user)):
    from medical_system.domain.auth.schemas import UserResponse
    
    user_dict = {
        'id': current_user.id,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'is_active': current_user.is_active,
        'is_admin': current_user.is_admin,
        'created_at': current_user.created_at,
        'metadata': current_user.metadata
    }
    
    return UserResponse(**user_dict)
