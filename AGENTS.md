# Agent Instructions for JobPortal Backend

This document contains conventions and guidelines for any AI agent interacting with this repository.

## Architecture & Stack
- **Framework**: Django 5 + Django REST Framework (DRF)
- **Database**: SQLite for development, PostgreSQL in production.
- **Background Tasks**: Celery with Redis broker.
- **Authentication**: JWT via `rest_framework_simplejwt`.
- **API Documentation**: OpenAPI generated with `drf-spectacular` (`openapi.yaml`).

## Coding Conventions
- **Typing**: Use PEP 484 type hints for all function signatures.
- **Docstrings**: Include clear, descriptive docstrings for classes, methods, and modules.
- **Logging**: Use the standard Python `logging` module to log significant events and errors. Do NOT use `print`.
- **Imports**: Organize imports logically: standard library, third-party packages, and local imports.
- **Permissions**: Follow least-privilege principles. Use DRF permission classes (`IsAuthenticated`, `IsEmployer`, `IsJobSeeker`, etc.).
- **Security**: Never commit secrets. Read sensitive data from environment variables.

## Testing & Quality Assurance
- **Tests**: Use `pytest`. Place tests in the `tests/` directory and ensure tests cover standard success and error paths.
- **Migrations**: Always generate migrations for any model changes using `python manage.py makemigrations`. Review the generated migration files before committing.
- **Validation**: Place business logic validation in models (`clean` method) or DRF serializers (`validate` method).

## API Design
- Follow standard RESTful practices.
- Define appropriate response schema using `drf_spectacular.utils.extend_schema`.
- All list endpoints should be paginated if returning more than a few objects.

## Important CLI Commands
- **Start server**: `python manage.py runserver`
- **Run migrations**: `python manage.py migrate`
- **Generate API schema**: `python manage.py spectacular --file openapi.yaml --validate`
- **Run tests**: `pytest`
