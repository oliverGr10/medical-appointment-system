from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from medical_system.domain.auth.config import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    roles: List[str] = []

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    is_active: bool = True
    metadata: Dict[str, Any] = {}
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('El nombre solo puede contener letras y espacios')
        return v.title()

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if v is not None and not v.replace(' ', '').isalpha():
            raise ValueError('El nombre solo puede contener letras y espacios')
        return v.title() if v else v

class UserInDB(UserBase):
    id: int
    is_admin: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserResponse(UserInDB):
    roles: List[str] = []
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, user):
        user_dict = user.to_dict() if hasattr(user, 'to_dict') else dict(user)
        user_dict['roles'] = user_dict.get('metadata', {}).get('roles', [])
        required_fields = ['id', 'email', 'first_name', 'last_name', 'created_at']
        for field in required_fields:
            if field not in user_dict:
                user_dict[field] = getattr(user, field, None)
        
        return cls(**user_dict)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRoleUpdate(BaseModel):
    roles: List[str]
    
    @validator('roles', each_item=True)
    def validate_roles(cls, v):
        valid_roles = [role for role in dir(UserRole) if not role.startswith('_')]
        if v not in valid_roles:
            raise ValueError(f'Rol no válido. Debe ser uno de: {", ".join(valid_roles)}')
        return v
