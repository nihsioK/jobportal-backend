"""Application configuration for applications."""

from __future__ import annotations

from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    """Configure the applications application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "applications"
