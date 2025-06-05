from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from medical_system.domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def list_all(
        self, 
        role: Optional[str] = None, 
        is_active: Optional[bool] = None,
        **filters
    ) -> List[User]:
        pass
    
    @abstractmethod
    def update_last_login(self, user_id: int, login_time: datetime) -> bool:
        pass
    
    @abstractmethod
    def exists_with_email(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        pass
