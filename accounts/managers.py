"""Custom managers for the accounts application."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from accounts.models import User


logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """Manager for the custom user model."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        """Create and persist a regular user."""
        if not email:
            logger.error("Attempted to create a user without an email address.")
            raise ValueError("Email is required.")

        normalized_email = self.normalize_email(email)
        logger.info("Creating user with email %s.", normalized_email)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)  # type: ignore
        user.full_clean()
        user.save(using=self._db)
        return user  # type: ignore

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        """Create and persist a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            logger.error("Invalid superuser flags supplied for email %s.", email)
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")

        logger.info("Creating superuser with email %s.", email)
        return self.create_user(email=email, password=password, **extra_fields)
