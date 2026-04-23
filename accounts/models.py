"""Models for the accounts application."""

from __future__ import annotations

import logging

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    objects = UserManager()

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


class UserProfile(models.Model):
    """Extended profile data for all users."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user_id"]

    def __str__(self) -> str:
        return f"Profile<{self.user.email}>"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):  # type: ignore
    """Automatically create a UserProfile when a User is created."""
    if created:
        UserProfile.objects.create(user=instance)


class Company(models.Model):
    """Company profile for employer users."""

    employer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="companies",
        limit_choices_to={"role": UserRole.EMPLOYER},
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    employee_count = models.CharField(max_length=50, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Company<{self.name}>"

