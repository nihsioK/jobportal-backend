# JobPortal API

JobPortal is a Django 5 and Django REST Framework backend for a job board MVP. This workspace currently exposes registration and JWT auth, self-service resume management, employer vacancy management, and job seeker application submission. OpenAPI documentation is available at `/api/schema/`, `/api/docs/`, and `/api/redoc/`.

## Architecture

```text
            +----------------------+
            |   API clients / UI   |
            +----------+-----------+
                       |
                       v
            +----------------------+
            | Django 5 + DRF API   |
            |  - accounts          |
            |  - resumes           |
            |  - vacancies         |
            |  - applications      |
            |  - OpenAPI docs      |
            +----+-------------+---+
                 |             |
                 v             v
       +----------------+   +------------------+
       | SQLite /       |   | Redis broker     |
       | PostgreSQL     |   | for Celery       |
       | via DATABASE_URL|  | via REDIS_URL    |
       +----------------+   +------------------+
```

## Quickstart

The default development configuration uses SQLite, so you can boot a working instance without external services.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Open the running service at:

- `http://127.0.0.1:8000/api/docs/` for Swagger UI
- `http://127.0.0.1:8000/api/redoc/` for ReDoc
- `http://127.0.0.1:8000/api/schema/?format=json` for the OpenAPI document

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | `jobportal.settings.dev` | Selects the Django settings module for local commands. |
| `DJANGO_SECRET_KEY` | `local-development-secret-key-please-change-12345` | Secret key for Django cryptographic signing. |
| `DJANGO_DEBUG` | `true` | Enables Django debug mode in development. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,testserver` | Comma-separated hostnames accepted by Django. |
| `DJANGO_TIME_ZONE` | `UTC` | Django application time zone. |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection string. Use PostgreSQL in shared environments. |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis broker URL for Celery tasks. |

## Authentication Flow

1. `POST /api/auth/register/` with `email`, `password`, and `role` to create a user.
2. `POST /api/auth/login/` with `email` and `password` to receive `access` and `refresh` JWTs.
3. Send `Authorization: Bearer <access>` for protected endpoints.
4. `POST /api/auth/refresh/` with `refresh` to obtain a new access token.

## API Cheatsheet

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register/` | Public | Register a job seeker, employer, or admin account. |
| `POST` | `/api/auth/login/` | Public | Exchange email and password for JWT tokens. |
| `POST` | `/api/auth/refresh/` | Public | Refresh an expired access token. |
| `GET` | `/api/resumes/me/` | Job seeker | Retrieve the authenticated seeker's resume. |
| `PATCH` | `/api/resumes/me/` | Job seeker | Update the authenticated seeker's resume fields. |
| `GET` | `/api/vacancies/` | Public | List vacancies with optional status, employer, and salary filters. |
| `GET` | `/api/vacancies/{id}/` | Public | Retrieve a single vacancy. |
| `POST` | `/api/vacancies/` | Employer | Create a vacancy owned by the authenticated employer. |
| `GET` | `/api/vacancies/mine/` | Employer | List vacancies owned by the authenticated employer. |
| `PATCH` | `/api/vacancies/{id}/` | Employer owner | Update one of your vacancies. |
| `DELETE` | `/api/vacancies/{id}/` | Employer owner | Delete one of your vacancies. |
| `POST` | `/api/applications/` | Job seeker | Apply to an open vacancy using the authenticated seeker's resume. |

## Verification

Run the automated checks and schema validation with:

```bash
pytest -q
python manage.py spectacular --file openapi.yaml --validate
```
