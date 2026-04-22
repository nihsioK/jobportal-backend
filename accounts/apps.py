"""Accounts application configuration."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """App configuration for accounts."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

