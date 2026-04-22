import pytest
from rest_framework import status

from applications.models import Application


@pytest.mark.django_db
def test_job_seeker_can_apply_to_vacancy(api_client, job_seeker_user, resume, vacancy):
    api_client.force_authenticate(user=job_seeker_user)
    response = api_client.post(
        "/api/applications/",
        data={
            "vacancy": vacancy.id,
            "resume": resume.id,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Application.objects.filter(resume=resume, vacancy=vacancy).exists()


@pytest.mark.django_db
def test_employer_cannot_apply_to_vacancy(api_client, employer_user, resume, vacancy):
    api_client.force_authenticate(user=employer_user)
    response = api_client.post(
        "/api/applications/",
        data={
            "vacancy": vacancy.id,
            "resume": resume.id,
        },
        format="json",
    )
    # Employer does not have IsJobSeeker permission
    assert response.status_code == status.HTTP_403_FORBIDDEN
