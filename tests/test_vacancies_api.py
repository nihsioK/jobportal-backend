"""API tests for the vacancies slice."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from vacancies.models import Vacancy, VacancyStatus


@pytest.fixture
def api_client() -> APIClient:
    """Provide a DRF API client."""
    return APIClient()


@pytest.fixture
def employer_user() -> User:
    """Create an employer user."""
    return User.objects.create_user(
        email="employer@example.com",
        password="password123",
        role=UserRole.EMPLOYER,
    )


@pytest.fixture
def second_employer_user() -> User:
    """Create another employer user."""
    return User.objects.create_user(
        email="employer-two@example.com",
        password="password123",
        role=UserRole.EMPLOYER,
    )


@pytest.fixture
def seeker_user() -> User:
    """Create a job seeker user."""
    return User.objects.create_user(
        email="seeker@example.com",
        password="password123",
        role=UserRole.JOB_SEEKER,
    )


@pytest.fixture
def vacancy(employer_user: User) -> Vacancy:
    """Create a baseline vacancy."""
    return Vacancy.objects.create(
        employer=employer_user,
        title="Backend Engineer",
        description="Build APIs",
        salary_min=1000,
        salary_max=2000,
        status=VacancyStatus.OPEN,
    )


@pytest.mark.django_db()
def test_public_list_and_detail_are_available_without_authentication(
    api_client: APIClient,
    vacancy: Vacancy,
) -> None:
    """Public readers can list and retrieve vacancies."""
    list_response = api_client.get("/api/vacancies/")
    detail_response = api_client.get(f"/api/vacancies/{vacancy.id}/")

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert list_response.data["results"][0]["id"] == vacancy.id
    assert detail_response.data["id"] == vacancy.id


@pytest.mark.django_db()
def test_public_list_supports_status_filter(
    api_client: APIClient,
    employer_user: User,
) -> None:
    """Public list filtering can narrow by status."""
    Vacancy.objects.create(
        employer=employer_user,
        title="Open Role",
        description="Open role description",
        salary_min=1000,
        salary_max=2000,
        status=VacancyStatus.OPEN,
    )
    Vacancy.objects.create(
        employer=employer_user,
        title="Closed Role",
        description="Closed role description",
        salary_min=1500,
        salary_max=2500,
        status=VacancyStatus.CLOSED,
    )

    response = api_client.get("/api/vacancies/", {"status": VacancyStatus.CLOSED})

    assert response.status_code == 200
    assert [item["status"] for item in response.data["results"]] == [VacancyStatus.CLOSED]


@pytest.mark.django_db()
def test_employer_can_create_vacancy(
    api_client: APIClient,
    employer_user: User,
) -> None:
    """Employers can create vacancies."""
    api_client.force_authenticate(user=employer_user)

    response = api_client.post(
        "/api/vacancies/",
        data={
            "title": "Platform Engineer",
            "description": "Maintain the platform",
            "salary_min": 3000,
            "salary_max": 5000,
            "status": VacancyStatus.OPEN,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["employer"] == employer_user.email
    assert Vacancy.objects.filter(employer=employer_user, title="Platform Engineer").exists()


@pytest.mark.django_db()
def test_non_employer_cannot_create_vacancy(
    api_client: APIClient,
    seeker_user: User,
) -> None:
    """Job seekers cannot create vacancies."""
    api_client.force_authenticate(user=seeker_user)

    response = api_client.post(
        "/api/vacancies/",
        data={
            "title": "Forbidden Vacancy",
            "description": "Should not be created",
            "salary_min": 1000,
            "salary_max": 2000,
            "status": VacancyStatus.OPEN,
        },
        format="json",
    )

    assert response.status_code == 403
    assert Vacancy.objects.count() == 0


@pytest.mark.django_db()
def test_salary_validation_rejects_invalid_range(
    api_client: APIClient,
    employer_user: User,
) -> None:
    """Salary min must be lower than salary max."""
    api_client.force_authenticate(user=employer_user)

    response = api_client.post(
        "/api/vacancies/",
        data={
            "title": "Invalid Salary Vacancy",
            "description": "Invalid salary",
            "salary_min": 5000,
            "salary_max": 5000,
            "status": VacancyStatus.OPEN,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "salary_min" in response.data


@pytest.mark.django_db()
def test_mine_returns_only_authenticated_employer_vacancies(
    api_client: APIClient,
    employer_user: User,
    second_employer_user: User,
) -> None:
    """Mine endpoint returns only the caller's vacancies."""
    own_vacancy = Vacancy.objects.create(
        employer=employer_user,
        title="Own Vacancy",
        description="Owned by caller",
        salary_min=1000,
        salary_max=2000,
        status=VacancyStatus.OPEN,
    )
    Vacancy.objects.create(
        employer=second_employer_user,
        title="Other Vacancy",
        description="Owned by another employer",
        salary_min=1000,
        salary_max=2000,
        status=VacancyStatus.OPEN,
    )
    api_client.force_authenticate(user=employer_user)

    response = api_client.get("/api/vacancies/mine/")

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [own_vacancy.id]


@pytest.mark.django_db()
def test_owner_can_update_and_delete_own_vacancy(
    api_client: APIClient,
    employer_user: User,
    vacancy: Vacancy,
) -> None:
    """Vacancy owners can update and delete their own records."""
    api_client.force_authenticate(user=employer_user)

    patch_response = api_client.patch(
        f"/api/vacancies/{vacancy.id}/",
        data={"title": "Updated Backend Engineer"},
        format="json",
    )
    delete_response = api_client.delete(f"/api/vacancies/{vacancy.id}/")

    assert patch_response.status_code == 200
    assert patch_response.data["title"] == "Updated Backend Engineer"
    assert delete_response.status_code == 204
    assert not Vacancy.objects.filter(id=vacancy.id).exists()


@pytest.mark.django_db()
def test_non_owner_employer_cannot_mutate_foreign_vacancy(
    api_client: APIClient,
    second_employer_user: User,
    vacancy: Vacancy,
) -> None:
    """Non-owner employers cannot update or delete foreign vacancies."""
    api_client.force_authenticate(user=second_employer_user)

    patch_response = api_client.patch(
        f"/api/vacancies/{vacancy.id}/",
        data={"title": "Illegal Update"},
        format="json",
    )
    delete_response = api_client.delete(f"/api/vacancies/{vacancy.id}/")

    assert patch_response.status_code == 403
    assert delete_response.status_code == 403
