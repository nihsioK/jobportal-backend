"""Tests for OpenAPI schema and documentation endpoints."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Provide a DRF API client."""
    return APIClient()


@pytest.mark.django_db()
def test_openapi_schema_includes_core_api_paths(api_client: APIClient) -> None:
    """The generated schema should document the main public API surface."""
    response = api_client.get("/api/schema/?format=json")

    assert response.status_code == 200
    assert "/api/auth/register/" in response.data["paths"]
    assert "/api/auth/login/" in response.data["paths"]
    assert "/api/auth/refresh/" in response.data["paths"]
    assert "/api/resumes/me/" in response.data["paths"]
    assert "/api/vacancies/" in response.data["paths"]
    assert "/api/applications/" in response.data["paths"]


@pytest.mark.django_db()
def test_docs_endpoints_render_html(api_client: APIClient) -> None:
    """Swagger UI and ReDoc should both be available."""
    swagger_response = api_client.get("/api/docs/")
    redoc_response = api_client.get("/api/redoc/")

    assert swagger_response.status_code == 200
    assert redoc_response.status_code == 200
    assert "text/html" in swagger_response["Content-Type"]
    assert "text/html" in redoc_response["Content-Type"]
