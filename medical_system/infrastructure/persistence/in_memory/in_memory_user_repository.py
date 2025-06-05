from datetime import datetime
from typing import Dict, List, Optional
from medical_system.domain.entities.user import User
from medical_system.domain.ports.repositories.user_repository import UserRepository

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1
        self._email_index: Dict[str, User] = {}

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        return self._email_index.get(email.lower())

    def save(self, user: User) -> User:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
            user.created_at = datetime.now()
        
        user.updated_at = datetime.now()
        user.email = user.email.lower()
        
        if user.id in self._users and self._users[user.id].email != user.email:
            old_user = self._users[user.id]
            if old_user.email in self._email_index:
                del self._email_index[old_user.email]
        
        self._users[user.id] = user
        self._email_index[user.email] = user
        return user

    def delete(self, user_id: int) -> bool:
        if user_id not in self._users:
            return False
            
        user = self._users[user_id]
        if user.email in self._email_index:
            del self._email_index[user.email]
            
        del self._users[user_id]
        return True

    def list_all(
        self, 
        role: Optional[str] = None, 
        is_active: Optional[bool] = None,
        **filters
    ) -> List[User]:
        users = list(self._users.values())
        
        if role is not None:
            users = [u for u in users if u.has_role(role)]
            
        if is_active is not None:
            users = [u for u in users if u.is_active == is_active]

        for key, value in filters.items():
            users = [u for u in users if hasattr(u, key) and getattr(u, key) == value]
            
        return users

    def update_last_login(self, user_id: int, login_time: datetime) -> bool:
        if user_id not in self._users:
            return False
            
        user = self._users[user_id]
        user.last_login = login_time
        return True

    def exists_with_email(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        email = email.lower()
        if email not in self._email_index:
            return False
            
        if exclude_user_id is not None:
            user = self._email_index[email]
            return user.id != exclude_user_id
            
        return True
