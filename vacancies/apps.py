"""Vacancies application configuration."""

from django.apps import AppConfig


class VacanciesConfig(AppConfig):
    """App configuration for vacancies."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "vacancies"
