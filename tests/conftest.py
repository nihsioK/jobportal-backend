import pytest
from rest_framework.test import APIClient

from tests.factories import ApplicationFactory, EmployerFactory, JobSeekerFactory, VacancyFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def job_seeker_user(db):
    return JobSeekerFactory()


@pytest.fixture
def employer_user(db):
    return EmployerFactory()


@pytest.fixture
def resume(db, job_seeker_user):
    # Resume is auto-created by signals for JOB_SEEKER
    return job_seeker_user.resume


@pytest.fixture
def vacancy(db, employer_user):
    return VacancyFactory(employer=employer_user)


@pytest.fixture
def application(db, resume, vacancy):
    return ApplicationFactory(resume=resume, vacancy=vacancy)
