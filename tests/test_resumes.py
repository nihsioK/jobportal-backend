"""Tests for resume ownership and self-service updates."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from resumes.models import Resume


class ResumeSignalTests(TestCase):
    """Unit tests for resume creation signals."""

    def test_job_seeker_creation_auto_creates_resume(self) -> None:
        """Creating a job seeker should create an empty resume."""
        user_model = get_user_model()

        seeker = user_model.objects.create_user(
            email="seeker@example.com",
            password="password123",
            role="JOB_SEEKER",
        )

        self.assertTrue(Resume.objects.filter(user=seeker).exists())

    def test_non_seeker_creation_does_not_auto_create_resume(self) -> None:
        """Creating a non-seeker should not create a resume."""
        user_model = get_user_model()

        employer = user_model.objects.create_user(
            email="employer@example.com",
            password="password123",
            role="EMPLOYER",
        )

        self.assertFalse(Resume.objects.filter(user=employer).exists())


class ResumeMeAPITests(TestCase):
    """Integration tests for the `/api/resumes/me/` endpoint."""

    client: APIClient

    def setUp(self) -> None:
        """Create users, resumes, and an API client for tests."""
        user_model = get_user_model()
        self.client = APIClient()
        self.seeker = user_model.objects.create_user(
            email="owner@example.com",
            password="password123",
            role="JOB_SEEKER",
        )
        self.other_seeker = user_model.objects.create_user(
            email="other@example.com",
            password="password123",
            role="JOB_SEEKER",
        )
        self.employer = user_model.objects.create_user(
            email="employer@example.com",
            password="password123",
            role="EMPLOYER",
        )
        self.url = "/api/resumes/me/"

    def authenticate(self, *, email: str) -> None:
        """Authenticate the test client as the requested user."""
        user_model = get_user_model()
        user = user_model.objects.get(email=email)
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_get_returns_authenticated_seekers_resume(self) -> None:
        """GET should return the authenticated seeker's own resume."""
        self.seeker.resume.title = "Platform Engineer"
        self.seeker.resume.summary = "Builds resilient APIs."
        self.seeker.resume.save()

        self.authenticate(email=self.seeker.email)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Platform Engineer")
        self.assertEqual(response.data["summary"], "Builds resilient APIs.")

    def test_get_returns_404_for_non_seeker(self) -> None:
        """GET should hide the resource from authenticated non-seekers."""
        self.authenticate(email=self.employer.email)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_nested_resume_fields(self) -> None:
        """PATCH should persist valid resume updates."""
        payload: dict[str, Any] = {
            "title": "Senior Backend Engineer",
            "summary": "Owns Django services.",
            "education": [
                {"institution": "State University", "degree": "BSc Computer Science"}
            ],
            "experience": [
                {"company": "Acme", "title": "Backend Engineer", "years": 4}
            ],
        }

        self.authenticate(email=self.seeker.email)
        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.seeker.resume.refresh_from_db()
        self.assertEqual(self.seeker.resume.title, payload["title"])
        self.assertEqual(self.seeker.resume.summary, payload["summary"])
        self.assertEqual(self.seeker.resume.education, payload["education"])
        self.assertEqual(self.seeker.resume.experience, payload["experience"])

    def test_patch_rejects_invalid_nested_json_schema(self) -> None:
        """PATCH should reject non-object items in nested JSON fields."""
        self.authenticate(email=self.seeker.email)
        response = self.client.patch(
            self.url,
            {"education": ["invalid-item"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("education", response.data)

    def test_endpoint_is_isolated_to_authenticated_user(self) -> None:
        """GET should never expose another seeker's resume."""
        self.seeker.resume.title = "Owner Resume"
        self.seeker.resume.save()
        self.other_seeker.resume.title = "Other Resume"
        self.other_seeker.resume.save()

        self.authenticate(email=self.seeker.email)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Owner Resume")

    def test_unauthenticated_get_is_rejected(self) -> None:
        """GET should require authentication."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
