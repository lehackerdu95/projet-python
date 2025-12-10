"""
App configuration for items application.
"""

from django.apps import AppConfig


class ItemsConfig(AppConfig):
    """Configuration class for items app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'items'
    verbose_name = 'Collections Management'
