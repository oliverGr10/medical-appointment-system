from fastapi import FastAPI, Depends, status, Request, HTTPException, APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from jose import JWTError, jwt
from .routers import appointments, doctors, patients, admin
from medical_system.domain.auth.service import AuthService
from medical_system.domain.auth.config import SECRET_KEY, ALGORITHM
from medical_system.domain.ports.repositories.user_repository import UserRepository
from medical_system.infrastructure.container import get_user_repository

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)

security_scheme = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Ingrese el token JWT con el prefijo 'Bearer ' (sin comillas)"
    }
}

swagger_js_url = "/static/swagger-ui-bundle.js"
swagger_css_url = "/static/swagger-ui.css"
swagger_favicon_url = "/static/favicon.ico"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado - Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

public_paths = {
    "/auth/login",
    "/auth/register",
    "/auth/refresh-token",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/static/"
}

app = FastAPI(
    title="Sistema de Citas Médicas API",
    description="API para la gestión de citas médicas con autenticación JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Soporte Técnico",
        "email": "soporte@clinica.com"
    },
    license_info={
        "name": "Licencia Propietaria",
        "url": "https://www.ejemplo.com/terminos"
    }
)

app.swagger_ui_parameters = {
    "docExpansion": "none",
    "operationsSorter": "method",
    "defaultModelsExpandDepth": -1,
    "persistAuthorization": True,
    "displayRequestDuration": True,
    "filter": True,
    "syntaxHighlight.theme": "monokai",
    "tryItOutEnabled": True,
    "requestSnippetsEnabled": True,
    "displayOperationId": True
}

security_schemes = {
    "Bearer": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "Ingrese el token JWT con el prefijo 'Bearer ' (sin comillas)"
    }
}

app.openapi_schema = None

@app.on_event("startup")
async def startup_event():
    if not app.openapi_schema:
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            contact=app.contact,
            license_info=app.license_info
        )
        

        openapi_schema["components"]["securitySchemes"] = security_schemes

        for path in openapi_schema.get("paths", {}).values():
            for method in path.values():
                if not any(tag in ["Autenticación", "Documentación"] for tag in method.get("tags", [])):
                    if "security" not in method:
                        method["security"] = [{"Bearer": []}]
        
        app.openapi_schema = openapi_schema
    
    return app.openapi_schema

def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
        init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": "swagger-ui",
        }
    )

app.get("/docs", include_in_schema=False)(custom_swagger_ui_html)

tags_metadata = [
    {
        "name": "Autenticación",
        "description": "🔑 Login, registro y gestión de tokens JWT"
    },
    {
        "name": "Pacientes",
        "description": "👥 Gestión de pacientes del sistema"
    },
    {
        "name": "Doctores",
        "description": "👨‍⚕️ Gestión de doctores y especialidades"
    },
    {
        "name": "Citas",
        "description": "📅 Gestión de citas médicas"
    }
]

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Ingrese el token JWT en el formato: Bearer <token>"
        }
    }
 
    for path_name, path_item in openapi_schema.get("paths", {}).items():
        if any(public_path in path_name for public_path in public_paths):
            continue

        for method in path_item.values():
            if isinstance(method, dict):
                if method.get("security") is None:
                    method["security"] = [{"bearerAuth": []}]
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

async def check_auth(request: Request, call_next):
    path = request.url.path

    normalized_path = path
    if path.startswith("/api"):
        normalized_path = path[4:]

    is_public = any(
        normalized_path == p or 
        normalized_path.startswith(p.rstrip('/') + '/') 
        for p in public_paths
    )
    
    if is_public or request.method == "OPTIONS":
        return await call_next(request)

    if not path.startswith("/api/") and not path.startswith("/auth/"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "No se proporcionó un token de autenticación. Por favor, inicie sesión primero."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = auth_header.split(" ")[1].strip()
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if datetime.fromtimestamp(payload.get("exp", 0)) < datetime.utcnow():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token expirado. Por favor, inicie sesión nuevamente."},
                headers={"WWW-Authenticate": "Bearer"}
            )

        if "sub" not in payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token inválido: falta el sujeto (sub)"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        request.state.user = payload
        
    except JWTError as e:
        print(f"[AUTH] Error al validar el token: {str(e)}")
        error_msg = f"Token inválido o expirado: {str(e)}"
        print(f"[AUTH] {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"[AUTH] Error inesperado al validar el token: {str(e)}")
        import traceback
        print(f"[AUTH] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al validar el token"
        )

    response = await call_next(request)
    return response

app.middleware("http")(check_auth)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.openapi = custom_openapi

app.swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": True,
    "clientId": "swagger-ui",
    "scopes": "read write",
}

@app.on_event("startup")
async def startup_event():
    user_repository = get_user_repository()
    
    auth_service = AuthService(user_repository)

    app.state.user_repository = user_repository
    app.state.auth_service = auth_service

    _create_default_admin(user_repository, auth_service)

def _create_default_admin(user_repository: UserRepository, auth_service: AuthService):
    admin_email = "admin@clinica.com"
    admin_password = "Admin123!"
    
    admin_user = user_repository.find_by_email(admin_email)
    if not admin_user:
        from medical_system.domain.entities.user import User
        from medical_system.domain.auth.config import UserRole
        
        try:
            from medical_system.domain.auth.schemas import UserCreate
            
            admin_create = UserCreate(
                email=admin_email,
                first_name="Administrador",
                last_name="Sistema",
                password=admin_password,
                password_confirm=admin_password,
                is_active=True,
                metadata={"roles": [UserRole.ADMIN]}
            )
            auth_service.create_user(admin_create)
        except Exception as e:
            print(f"Error al crear usuario administrador: {e}")

from medical_system.infrastructure.container import get_user_repository
from medical_system.domain.auth.service import AuthService

user_repository = get_user_repository()
auth_service = AuthService(user_repository)
app.state.auth_service = auth_service

api_router = APIRouter(prefix="/api")

from .routers import auth as auth_router
app.include_router(auth_router.router, prefix="/api")
print("Rutas de autenticación incluidas correctamente")

api_router.include_router(
    patients.router,
    prefix="/patients",
    tags=["Pacientes"],
    dependencies=[Depends(oauth2_scheme)],
    responses={"404": {"description": "No encontrado"}},
)

api_router.include_router(
    doctors.router,
    prefix="/doctors",
    tags=["Doctores"],
    dependencies=[Depends(oauth2_scheme)],
    responses={"404": {"description": "No encontrado"}},
)

api_router.include_router(
    appointments.router,
    prefix="/appointments",
    tags=["Citas"],
    dependencies=[Depends(oauth2_scheme)],
    responses={"404": {"description": "No encontrado"}},
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administración"],
    dependencies=[Depends(oauth2_scheme)],
    responses={"404": {"description": "No encontrado"}},
)

app.mount("/static", StaticFiles(directory="medical_system/static"), name="static")

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "El servicio está funcionando correctamente"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("medical_system.interfaces.api.main:app", host="0.0.0.0", port=8000, reload=True)