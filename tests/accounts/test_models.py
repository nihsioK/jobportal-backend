import pytest
from django.contrib.auth import get_user_model

from accounts.models import UserRole

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="test@example.com", password="password", role=UserRole.JOB_SEEKER)
    assert user.email == "test@example.com"
    assert user.role == UserRole.JOB_SEEKER
    assert user.check_password("password")


@pytest.mark.django_db
def test_create_user_without_email_fails():
    with pytest.raises(ValueError, match="Email is required"):
        User.objects.create_user(email="", password="password", role=UserRole.JOB_SEEKER)


@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(email="admin@example.com", password="password")
    assert user.email == "admin@example.com"
    assert user.role == UserRole.ADMIN
    assert user.is_staff
    assert user.is_superuser
