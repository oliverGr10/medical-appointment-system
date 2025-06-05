from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def has_role(self, role: str) -> bool:

        roles = self.metadata.get('roles', [])
        return role in roles
    
    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()
    
    def update_last_login(self) -> None:
        self.last_login = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'metadata': self.metadata
        }
