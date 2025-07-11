"""
repository.py: Defines the abstract Repository interface and an in-memory implementation.

Provides a uniform API for data persistence across different model types.
"""

from abc import ABC, abstractmethod

class Repository(ABC):
    """Abstract base class for a generic data repository."""

    @abstractmethod
    def add(self, obj):
        """
        Add a new object to the repository.

        Args:
            obj: The object to add, must have a unique `id` attribute.
        """
        pass

    @abstractmethod
    def get(self, obj_id):
        """
        Retrieve an object by its ID.

        Args:
            obj_id: The unique identifier of the object.

        Returns:
            The object if found, else None.
        """
        pass

    @abstractmethod
    def get_all(self):
        """
        List all objects in the repository.

        Returns:
            A list of all stored objects.
        """
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """
        Update attributes of an existing object.

        Args:
            obj_id: The unique identifier of the object to update.
            data: A dict of attributes to modify on the object.
        """
        pass

    @abstractmethod
    def delete(self, obj_id):
        """
        Remove an object from the repository by its ID.

        Args:
            obj_id: The unique identifier of the object to delete.
        """
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """
        Find the first object matching a given attribute value.

        Args:
            attr_name: Name of the attribute to match.
            attr_value: Value of the attribute to search for.

        Returns:
            The first matching object, or None if no match is found.
        """
        pass


class InMemoryRepository(Repository):
    """
    In-memory implementation of Repository.

    Stores objects in a dictionary keyed by their `id` attribute.
    """

    def __init__(self):
        """Initialize an empty in-memory storage."""
        self._storage = {}

    def add(self, obj):
        """
        Add an object to the in-memory storage.

        Args:
            obj: The object to store, must have a unique `id` attribute.
        """
        self._storage[obj.id] = obj

    def get(self, obj_id):
        """
        Retrieve an object by its ID from storage.

        Args:
            obj_id: The unique identifier of the object.

        Returns:
            The object if found, else None.
        """
        return self._storage.get(obj_id)

    def get_all(self):
        """
        List all objects currently stored.

        Returns:
            A list of all stored objects.
        """
        return list(self._storage.values())

    def update(self, obj_id, data):
        """
        Update an existing object's attributes.

        Args:
            obj_id: The unique identifier of the object to update.
            data: A dict of attributes to set on the object.
        """
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        """
        Delete an object from storage by its ID.

        Args:
            obj_id: The unique identifier of the object to remove.
        """
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve the first object where a given attribute matches a value.

        Args:
            attr_name: Name of the attribute to filter by.
            attr_value: Value to match on the attribute.

        Returns:
            The first matching object, or None if none found.
        """
        return next(
            (
                obj
                for obj in self._storage.values()
                if getattr(obj, attr_name) == attr_value
            ),
            None,
        )
