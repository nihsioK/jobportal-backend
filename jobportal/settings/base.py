"""Base Django settings for the JobPortal project."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import dj_database_url


logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _get_bool(name: str, default: bool) -> bool:
    """Read a boolean flag from environment variables."""
    raw_value = os.getenv(name)
    if raw_value is None:
        logger.info("Environment variable %s not set; using default %s.", name, default)
        return default

    value = raw_value.strip().lower() in {"1", "true", "yes", "on"}
    logger.info("Environment variable %s resolved to %s.", name, value)
    return value


def _get_allowed_hosts() -> list[str]:
    """Resolve allowed hosts from the environment."""
    raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
    hosts = [host.strip() for host in raw_hosts.split(",") if host.strip()]
    logger.info("Resolved allowed hosts: %s.", hosts)
    return hosts


def _get_database_config() -> dict[str, Any]:
    """Build the database configuration from the environment."""
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
    logger.info("Configuring database from DATABASE_URL with scheme %s.", database_url.split(':', maxsplit=1)[0])
    return {
        "default": dj_database_url.parse(
            database_url,
            conn_max_age=600,
        ),
    }


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "local-development-secret-key-please-change-12345")
DEBUG = _get_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = _get_allowed_hosts()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_celery_beat",
    "accounts.apps.AccountsConfig",
    "resumes.apps.ResumesConfig",
    "vacancies.apps.VacanciesConfig",
    "applications.apps.ApplicationsConfig",
    "search.apps.SearchConfig",
    "notifications.apps.NotificationsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jobportal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jobportal.wsgi.application"
ASGI_APPLICATION = "jobportal.asgi.application"
DATABASES = _get_database_config()

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "JobPortal API",
    "DESCRIPTION": (
        "OpenAPI schema for the JobPortal MVP.\n\n"
        "Authentication flow:\n"
        "1. POST `/api/auth/register/` to create a user.\n"
        "2. POST `/api/auth/login/` with email and password to obtain JWTs.\n"
        "3. Send `Authorization: Bearer <access>` to protected endpoints.\n"
        "4. POST `/api/auth/refresh/` to rotate an expired access token."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api",
    "TAGS": [
        {"name": "accounts", "description": "User registration and JWT authentication."},
        {"name": "resumes", "description": "Job seeker resume self-service endpoints."},
        {"name": "vacancies", "description": "Vacancy discovery and employer vacancy management."},
        {"name": "applications", "description": "Job application submission endpoints."},
    ],
}

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# MeiliSearch Configuration
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", "masterKey")
MEILI_VACANCY_INDEX = "vacancies"
# Caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    }
}

# Celery
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
