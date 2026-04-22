"""App configuration for resumes."""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ResumesConfig(AppConfig):
    """Configuration for the resumes application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "resumes"

    def ready(self) -> None:
        """Import signal handlers when the app is ready."""
        logger.info("Loading resume signal handlers.")
        import resumes.signals  # noqa: F401
