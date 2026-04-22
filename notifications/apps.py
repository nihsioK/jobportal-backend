"""Notifications application configuration."""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """App configuration for notifications."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
