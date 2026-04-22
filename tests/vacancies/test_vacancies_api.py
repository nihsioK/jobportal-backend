import pytest
from rest_framework import status

from vacancies.models import Vacancy, VacancyStatus


@pytest.mark.django_db
def test_public_list_and_detail_are_available_without_authentication(api_client, vacancy):
    list_response = api_client.get("/api/vacancies/")
    detail_response = api_client.get(f"/api/vacancies/{vacancy.id}/")
    assert list_response.status_code == status.HTTP_200_OK
    assert detail_response.status_code == status.HTTP_200_OK
    assert list_response.data["results"][0]["id"] == vacancy.id


@pytest.mark.django_db
def test_employer_can_create_vacancy(api_client, employer_user):
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
    assert response.status_code == status.HTTP_201_CREATED
    assert Vacancy.objects.filter(employer=employer_user, title="Platform Engineer").exists()


@pytest.mark.django_db
def test_salary_validation_rejects_invalid_range(api_client, employer_user):
    api_client.force_authenticate(user=employer_user)
    response = api_client.post(
        "/api/vacancies/",
        data={
            "title": "Invalid Salary",
            "description": "Invalid salary",
            "salary_min": 5000,
            "salary_max": 5000,
            "status": VacancyStatus.OPEN,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_mine_returns_only_authenticated_employer_vacancies(api_client, employer_user, vacancy):
    # vacancy is owned by employer_user by default from conftest.py
    api_client.force_authenticate(user=employer_user)
    response = api_client.get("/api/vacancies/mine/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == vacancy.id
