"""Tests for vacancy search functionality."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status

from accounts.models import UserRole
from vacancies.models import Vacancy, VacancyStatus


@pytest.fixture
def employer(db, django_user_model):
    """Create an employer user."""
    return django_user_model.objects.create_user(
        email="employer@example.com",
        password="password123",
        role=UserRole.EMPLOYER,
    )


@pytest.fixture
def vacancy(db, employer):
    """Create a vacancy."""
    return Vacancy.objects.create(
        employer=employer,
        title="Python Developer",
        description="Write cool code.",
        salary_min=50000,
        salary_max=100000,
        status=VacancyStatus.OPEN,
    )


@pytest.mark.django_db
@patch("search.signals.upsert_vacancy")
def test_vacancy_indexing_on_save(mock_upsert, employer):
    """Test that saving a vacancy triggers indexing."""
    # Create vacancy - triggers post_save signal
    vacancy = Vacancy.objects.create(
        employer=employer,
        title="Backend Engineer",
        description="Django expert.",
        salary_min=60000,
        salary_max=120000,
    )

    assert mock_upsert.called
    mock_upsert.assert_called_with(vacancy)


@pytest.mark.django_db
@patch("search.signals.delete_vacancy")
def test_vacancy_deletion_removes_from_index(mock_delete, employer):
    """Test that deleting a vacancy removes it from search."""
    # Patch upsert to avoid connection error during creation
    with patch("search.signals.upsert_vacancy"):
        vacancy = Vacancy.objects.create(
            employer=employer,
            title="Temp",
            description="Temp",
            salary_min=100,
            salary_max=200,
        )

    vacancy_id = vacancy.id
    vacancy.delete()

    assert mock_delete.called
    mock_delete.assert_called_with(vacancy_id)


@pytest.mark.django_db
@patch("search.views.get_vacancy_index")
def test_vacancy_search_view(mock_get_index, client):
    """Test the search API endpoint."""
    mock_index = MagicMock()
    mock_get_index.return_value = mock_index
    
    mock_index.search.return_value = {
        "hits": [
            {
                "id": 1,
                "title": "Mock Developer",
                "description": "Mocking stuff.",
                "salary_min": 50000,
                "salary_max": 80000,
                "status": "OPEN",
                "employer_id": 1,
                "created_at": 1600000000.0,
                "updated_at": 1600000000.0,
            }
        ]
    }

    url = reverse("search:vacancy-search")
    response = client.get(url, {"q": "Mock"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Mock Developer"
    assert mock_index.search.called
    args, kwargs = mock_index.search.call_args
    assert args[0] == "Mock"


@pytest.mark.django_db
@patch("search.views.get_vacancy_index")
def test_vacancy_search_filters(mock_get_index, client):
    """Test that filters are correctly passed to MeiliSearch."""
    mock_index = MagicMock()
    mock_get_index.return_value = mock_index
    mock_index.search.return_value = {"hits": []}

    url = reverse("search:vacancy-search")
    params = {
        "q": "Python",
        "status": "OPEN",
        "salary_min": 50000,
        "salary_max": 100000,
        "employer_id": 1,
    }
    client.get(url, params)

    assert mock_index.search.called
    args, _ = mock_index.search.call_args
    search_params = args[1]
    filters = search_params["filter"]
    assert "status = OPEN" in filters
    assert "salary_min >= 50000" in filters
    assert "salary_max <= 100000" in filters
    assert "employer_id = 1" in filters
