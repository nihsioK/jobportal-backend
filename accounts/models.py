"""Models for the accounts application."""

from __future__ import annotations

import logging

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from accounts.managers import UserManager

logger = logging.getLogger(__name__)


class UserRole(models.TextChoices):
    """Available user roles."""

    JOB_SEEKER = "JOB_SEEKER", "Job seeker"
    EMPLOYER = "EMPLOYER", "Employer"
    ADMIN = "ADMIN", "Admin"


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model keyed by email identity."""

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = ["role"]

    class Meta:
        ordering = ["email"]

    def clean(self) -> None:
        """Validate the user instance."""
        super().clean()
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)
            logger.info("Normalized email for user %s.", self.email)

        if self.role not in UserRole.values:
            logger.error("Invalid role %s provided for user %s.", self.role, self.email)
            raise ValidationError({"role": "Invalid role."})
