# app/services/facade.py

from datetime import datetime
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.host import Host


class HBnBFacade:
    def __init__(self):
        # Repositories for each model
        self.user_repo    = InMemoryRepository()
        self.host_repo    = InMemoryRepository()
        self.place_repo   = InMemoryRepository()   # stubbed for later
        self.review_repo  = InMemoryRepository()   # stubbed for later
        self.amenity_repo = InMemoryRepository()   # stubbed for later

    # ----------------------- USERS ----------------------------

    def create_user(self, user_data):
        """Create a new user, error on duplicate email."""
        if self.user_repo.get_by_attribute('email', user_data['email']):
            raise ValueError(f"Email '{user_data['email']}' is already in use")

        user = User(
            first_name=user_data['first_name'],
            last_name =user_data['last_name'],
            email     =user_data['email'],
            is_admin  =user_data.get('is_admin', False)
        )
        self.user_repo.add(user)

        return {
            'id'         : user.id,
            'first_name' : user.first_name,
            'last_name'  : user.last_name,
            'email'      : user.email,
            'is_admin'   : user.is_admin
        }

    def get_all_users(self):
        """Return list of all users."""
        return [
            {
                'id'         : u.id,
                'first_name' : u.first_name,
                'last_name'  : u.last_name,
                'email'      : u.email,
                'is_admin'   : u.is_admin
            }
            for u in self.user_repo.get_all()
        ]

    def get_user(self, user_id):
        """Fetch a user by ID or raise KeyError."""
        u = self.user_repo.get(user_id)
        if not u:
            raise KeyError(f"User not found: {user_id}")
        return {
            'id'         : u.id,
            'first_name' : u.first_name,
            'last_name'  : u.last_name,
            'email'      : u.email,
            'is_admin'   : u.is_admin
        }

    def update_user(self, user_id, user_data):
        """Update fields on an existing user, enforce email uniqueness."""
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
            'id'         : u.id,
            'first_name' : u.first_name,
            'last_name'  : u.last_name,
            'email'      : u.email,
            'is_admin'   : u.is_admin
        }

    def delete_user(self, user_id):
        """Remove a user by ID or raise KeyError."""
        if not self.user_repo.get(user_id):
            raise KeyError(f"User not found: {user_id}")
        self.user_repo.delete(user_id)

    # ----------------------- HOSTS ----------------------------

    def create_host(self, host_data):
        """Create a new host, error on duplicate email."""
        if self.host_repo.get_by_attribute('email', host_data['email']):
            raise ValueError(f"Email '{host_data['email']}' already in use")

        host = Host(
            first_name=host_data['first_name'],
            last_name =host_data['last_name'],
            email     =host_data['email']
        )
        self.host_repo.add(host)

        return {
            'id'         : host.id,
            'first_name' : host.first_name,
            'last_name'  : host.last_name,
            'email'      : host.email
        }

    def get_all_hosts(self):
        """Return list of all hosts."""
        return [
            {
                'id'         : h.id,
                'first_name' : h.first_name,
                'last_name'  : h.last_name,
                'email'      : h.email
            }
            for h in self.host_repo.get_all()
        ]

    def get_host(self, host_id):
        """Fetch a host by ID or raise KeyError."""
        h = self.host_repo.get(host_id)
        if not h:
            raise KeyError(f"Host not found: {host_id}")
        return {
            'id'         : h.id,
            'first_name' : h.first_name,
            'last_name'  : h.last_name,
            'email'      : h.email
        }

    def update_host(self, host_id, host_data):
        """Update fields on an existing host, enforce email uniqueness."""
        h = self.host_repo.get(host_id)
        if not h:
            raise KeyError(f"Host not found: {host_id}")

        new_email = host_data.get('email')
        if new_email and new_email != h.email:
            if self.host_repo.get_by_attribute('email', new_email):
                raise ValueError(f"Email '{new_email}' already in use")

        for field in ('first_name', 'last_name', 'email'):
            if field in host_data:
                setattr(h, field, host_data[field])
        h.updated_at = datetime.now()

        return {
            'id'         : h.id,
            'first_name' : h.first_name,
            'last_name'  : h.last_name,
            'email'      : h.email
        }

    def delete_host(self, host_id):
        """Remove a host by ID or raise KeyError."""
        if not self.host_repo.get(host_id):
            raise KeyError(f"Host not found: {host_id}")
        self.host_repo.delete(host_id)
