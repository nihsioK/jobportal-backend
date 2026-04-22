"""Search application configuration."""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    """App configuration for search."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "search"

