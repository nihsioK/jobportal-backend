"""Integration tests for application creation."""

from __future__ import annotations

import logging

import pytest
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from applications.models import Application, ApplicationStatus
from vacancies.models import Vacancy, VacancyStatus


logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db()


def create_user(email: str, role: str) -> User:
    """Create a user with the given role."""
    logger.info("Creating test user.", extra={"email": email, "role": role})
    return User.objects.create_user(email=email, password="secret12345", role=role)


def create_vacancy(employer: User, status: str = VacancyStatus.OPEN) -> Vacancy:
    """Create a vacancy for tests."""
    logger.info("Creating test vacancy.", extra={"employer_id": employer.pk, "status": status})
    return Vacancy.objects.create(
        employer=employer,
        title="Backend Engineer",
        description="Build APIs.",
        salary_min=1000,
        salary_max=2000,
        status=status,
    )


def test_job_seeker_can_create_pending_application() -> None:
    """A job seeker can apply to an open vacancy."""
    logger.info("Running happy-path application test.")
    employer = create_user(email="employer@example.com", role=UserRole.EMPLOYER)
    seeker = create_user(email="seeker@example.com", role=UserRole.JOB_SEEKER)
    vacancy = create_vacancy(employer=employer)
    client = APIClient()
    client.force_authenticate(user=seeker)

    response = client.post("/api/applications/", data={"vacancy": vacancy.pk}, format="json")

    assert response.status_code == 201
    assert response.data["status"] == ApplicationStatus.PENDING
    application = Application.objects.get()
    assert application.resume == seeker.resume
    assert application.vacancy == vacancy
    assert application.status == ApplicationStatus.PENDING


def test_duplicate_application_returns_400() -> None:
    """A duplicate application is rejected."""
    logger.info("Running duplicate application test.")
    employer = create_user(email="duplicate-employer@example.com", role=UserRole.EMPLOYER)
    seeker = create_user(email="duplicate-seeker@example.com", role=UserRole.JOB_SEEKER)
    vacancy = create_vacancy(employer=employer)
    Application.objects.create(resume=seeker.resume, vacancy=vacancy)
    client = APIClient()
    client.force_authenticate(user=seeker)

    response = client.post("/api/applications/", data={"vacancy": vacancy.pk}, format="json")

    assert response.status_code == 400
    assert "already applied" in str(response.data).lower()


def test_only_job_seeker_can_post_application() -> None:
    """Only users with the job seeker role can create applications."""
    logger.info("Running job seeker permission test.")
    employer = create_user(email="poster@example.com", role=UserRole.EMPLOYER)
    vacancy_owner = create_user(email="other-employer@example.com", role=UserRole.EMPLOYER)
    vacancy = create_vacancy(employer=vacancy_owner)
    client = APIClient()
    client.force_authenticate(user=employer)

    response = client.post("/api/applications/", data={"vacancy": vacancy.pk}, format="json")

    assert response.status_code == 403


def test_closed_vacancy_is_rejected() -> None:
    """Applications to closed vacancies are rejected."""
    logger.info("Running closed vacancy rejection test.")
    employer = create_user(email="closed-employer@example.com", role=UserRole.EMPLOYER)
    seeker = create_user(email="closed-seeker@example.com", role=UserRole.JOB_SEEKER)
    vacancy = create_vacancy(employer=employer, status=VacancyStatus.CLOSED)
    client = APIClient()
    client.force_authenticate(user=seeker)

    response = client.post("/api/applications/", data={"vacancy": vacancy.pk}, format="json")

    assert response.status_code == 400
    assert "open vacancies" in str(response.data).lower()
