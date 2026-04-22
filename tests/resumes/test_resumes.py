import pytest
from rest_framework import status

from resumes.models import Resume


@pytest.mark.django_db
def test_job_seeker_creation_auto_creates_resume(job_seeker_user):
    assert Resume.objects.filter(user=job_seeker_user).exists()


@pytest.mark.django_db
def test_employer_creation_does_not_auto_create_resume(employer_user):
    assert not Resume.objects.filter(user=employer_user).exists()


@pytest.mark.django_db
def test_get_returns_authenticated_seekers_resume(api_client, job_seeker_user, resume):
    resume.title = "Platform Engineer"
    resume.save()
    api_client.force_authenticate(user=job_seeker_user)
    response = api_client.get("/api/resumes/me/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Platform Engineer"


@pytest.mark.django_db
def test_get_returns_404_for_non_seeker(api_client, employer_user):
    api_client.force_authenticate(user=employer_user)
    response = api_client.get("/api/resumes/me/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_updates_nested_resume_fields(api_client, job_seeker_user, resume):
    payload = {
        "title": "Senior Backend Engineer",
        "summary": "Owns Django services.",
        "education": [{"institution": "State University", "degree": "BSc Computer Science"}],
        "experience": [{"company": "Acme", "title": "Backend Engineer", "years": 4}],
    }
    api_client.force_authenticate(user=job_seeker_user)
    response = api_client.patch("/api/resumes/me/", payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    resume.refresh_from_db()
    assert resume.title == payload["title"]
    assert resume.summary == payload["summary"]


@pytest.mark.django_db
def test_unauthenticated_get_is_rejected(api_client):
    response = api_client.get("/api/resumes/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
