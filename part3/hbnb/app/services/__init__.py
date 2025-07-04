"""
__init__.py: Package initializer for the HBnB application.

This module creates and exposes a singleton facade instance that provides
unified access to all HBnB services and repositories.
"""

from app.services.facade import HBnBFacade

facade = HBnBFacade()
"""HBnBFacade instance providing unified access to all application operations."""
