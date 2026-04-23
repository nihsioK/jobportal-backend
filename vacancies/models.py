"""Models for the vacancies application."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import UserRole
from core.models import City, JobCategory, Skill


logger = logging.getLogger(__name__)


class VacancyStatus(models.TextChoices):
    """Available vacancy lifecycle states."""

    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "Closed"


class EmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", "Full Time"
    PART_TIME = "PART_TIME", "Part Time"
    CONTRACT = "CONTRACT", "Contract"
    INTERNSHIP = "INTERNSHIP", "Internship"
    REMOTE = "REMOTE", "Remote"


class ExperienceLevel(models.TextChoices):
    NO_EXPERIENCE = "NO_EXPERIENCE", "No Experience"
    JUNIOR = "JUNIOR", "Junior (1-3 years)"
    MID_LEVEL = "MID_LEVEL", "Mid-Level (3-5 years)"
    SENIOR = "SENIOR", "Senior (5+ years)"
    LEAD = "LEAD", "Lead / Manager"


class Vacancy(models.Model):
    """Employer-owned job vacancy."""

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vacancies",
        limit_choices_to={"role": UserRole.EMPLOYER},
    )
    title = models.CharField(max_length=255)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    employment_type = models.CharField(max_length=32, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    experience_level = models.CharField(max_length=32, choices=ExperienceLevel.choices, default=ExperienceLevel.MID_LEVEL)
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
        super().save(*args, **kwargs)


class SavedVacancy(models.Model):
    """Vacancy bookmarked by a job seeker."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_vacancies",
        limit_choices_to={"role": UserRole.JOB_SEEKER},
    )
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "vacancy"], name="unique_saved_vacancy"),
        ]

    def __str__(self) -> str:
        return f"SavedVacancy<{self.user_id}: {self.vacancy_id}>"

