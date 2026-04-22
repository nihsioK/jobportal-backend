"""Models for the vacancies application."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import UserRole

logger = logging.getLogger(__name__)


class VacancyStatus(models.TextChoices):
    """Available vacancy lifecycle states."""

    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "Closed"


class Vacancy(models.Model):
    """Employer-owned job vacancy."""

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vacancies",
        limit_choices_to={"role": UserRole.EMPLOYER},
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    salary_min = models.PositiveIntegerField()
    salary_max = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=VacancyStatus.choices, default=VacancyStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self) -> None:
        """Validate the salary range for the vacancy."""
        super().clean()
        if self.salary_min >= self.salary_max:
            logger.error(
                "Vacancy salary validation failed for title %s: salary_min=%s salary_max=%s.",
                self.title,
                self.salary_min,
                self.salary_max,
            )
            raise ValidationError({"salary_min": "salary_min must be less than salary_max."})

        logger.info("Validated vacancy salary range for title %s.", self.title)

    def save(self, *args: object, **kwargs: object) -> None:
        """Validate and persist the vacancy."""
        logger.info("Saving vacancy %s.", self.title)
        self.full_clean()
        super().save(*args, **kwargs) # type: ignore
