"""Data models for job applications."""

from __future__ import annotations

from django.db import models


class ApplicationStatus(models.TextChoices):
    """Lifecycle states for an application."""

    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"


class Application(models.Model):
    """Connect a resume to a vacancy."""

    resume = models.ForeignKey("resumes.Resume", related_name="applications", on_delete=models.CASCADE)
    vacancy = models.ForeignKey("vacancies.Vacancy", related_name="applications", on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("resume", "vacancy"), name="unique_resume_vacancy"),
        ]
