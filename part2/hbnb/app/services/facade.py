# app/services/facade.py
from typing import Optional, Dict, Any, List
from app.models.user import User
from app.persistence.repository import InMemoryRepository

class HBNBFacade:
    """
    Single facade exposing only User operations (Task 2).
    Wraps your InMemoryRepository and your User model.
    """

    def __init__(self):
        self.user_repo = InMemoryRepository()

    def create_user(self, user_data: Dict[str, Any]) -> User:
        # Enforce email uniqueness
        if self.user_repo.get_by_attribute('email', user_data.get('email')):
            raise ValueError("email must be unique")
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_attribute('email', email)

    def list_users(self) -> List[User]:
        return self.user_repo.get_all()

    def update_user(self, user_id: str, data: Dict[str, Any]) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        # If changing email, ensure unique
        if 'email' in data:
            existing = self.user_repo.get_by_attribute('email', data['email'])
            if existing and existing.id != user_id:
                raise ValueError("email must be unique")
        self.user_repo.update(user_id, data)
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> bool:
        return self.user_repo.delete(user_id)
