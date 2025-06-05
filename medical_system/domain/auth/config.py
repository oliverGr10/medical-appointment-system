import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    SECRET_KEY = "test_secret_key_123456789012345678901234567890"
else:
    DEFAULT_SECRET_KEY = "mi_clave_secreta_muy_larga_y_segura_para_entorno_de_desarrollo_12345!@#"
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    if len(SECRET_KEY) < 32:
        SECRET_KEY = SECRET_KEY.ljust(32, '0')[:32]

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class UserRole:
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

PWD_CONTEXT = {
    "schemes": ["bcrypt"],
    "deprecated": "auto"
}

def get_password_hash(password: str) -> str:
    from passlib.context import CryptContext
    pwd_context = CryptContext(**PWD_CONTEXT)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(**PWD_CONTEXT)
    return pwd_context.verify(plain_password, hashed_password)

def get_token_expires_delta(minutes: Optional[int] = None) -> datetime:
    if minutes is None:
        minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    return datetime.utcnow() + timedelta(minutes=minutes)

def get_refresh_token_expires_delta() -> datetime:
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
