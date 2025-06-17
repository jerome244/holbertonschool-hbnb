from app.persistence.repository import InMemoryRepository
from app.models.user import User
from datetime import datetime

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        # … place/review/amenity repos …

    def create_user(self, user_data):
        # 1) Check for duplicate email
        if self.user_repo.get_by_attribute('email', user_data['email']):
            raise ValueError(f"Email '{user_data['email']}' is already in use")

        # 2) Instantiate and persist
        user = User(
            first_name=user_data['first_name'],
            last_name =user_data['last_name'],
            email     =user_data['email'],
            is_admin  =user_data.get('is_admin', False)
        )
        self.user_repo.add(user)

        # 3) Return a JSON-serializable dict
        return {
            'id'        : user.id,
            'first_name': user.first_name,
            'last_name' : user.last_name,
            'email'     : user.email,
            'is_admin'  : user.is_admin
        }

    def get_all_users(self):
        return [
            {
              'id'        : u.id,
              'first_name': u.first_name,
              'last_name' : u.last_name,
              'email'     : u.email,
              'is_admin'  : u.is_admin
            }
            for u in self.user_repo.get_all()
        ]

    def get_user(self, user_id):
        u = self.user_repo.get(user_id)
        if not u:
            raise KeyError(f"User not found: {user_id}")
        return {
            'id'        : u.id,
            'first_name': u.first_name,
            'last_name' : u.last_name,
            'email'     : u.email,
            'is_admin'  : u.is_admin
        }

    def update_user(self, user_id, user_data):
        u = self.user_repo.get(user_id)
        if not u:
            raise KeyError(f"User not found: {user_id}")

        new_email = user_data.get('email')
        if new_email and new_email != u.email:
            if self.user_repo.get_by_attribute('email', new_email):
                raise ValueError(f"Email '{new_email}' is already in use")

        for field in ('first_name', 'last_name', 'email', 'is_admin'):
            if field in user_data:
                setattr(u, field, user_data[field])
        u.updated_at = datetime.now()

        return {
            'id'        : u.id,
            'first_name': u.first_name,
            'last_name' : u.last_name,
            'email'     : u.email,
            'is_admin'  : u.is_admin
        }

    def delete_user(self, user_id):
        if not self.user_repo.get(user_id):
            raise KeyError(f"User not found: {user_id}")
        self.user_repo.delete(user_id)
