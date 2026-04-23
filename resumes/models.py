"""Models for resume ownership and profile data."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from accounts.models import UserRole
from core.models import City, Skill


class ResumeVisibility(models.TextChoices):
    PUBLIC = "PUBLIC", "Public"
    HIDDEN = "HIDDEN", "Hidden"
    ONLY_BY_LINK = "ONLY_BY_LINK", "Only by link"


class Resume(models.Model):
    """Resume owned by a job seeker. A user can have multiple resumes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    desired_salary = models.PositiveIntegerField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    visibility = models.CharField(max_length=32, choices=ResumeVisibility.choices, default=ResumeVisibility.PUBLIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Resume<{self.id}: {self.title}>"


class WorkExperience(models.Model):
    """Structured work experience for a resume."""

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experience")
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]


class Education(models.Model):
    """Structured education for a resume."""

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-start_year"]


class Language(models.Model):
    """Language proficiency."""

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="languages")
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=50)


class Certificate(models.Model):
    """Certifications and courses."""

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="certificates")
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True, blank=True)


class SavedResume(models.Model):
    """Resume bookmarked by an employer."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_resumes",
        limit_choices_to={"role": UserRole.EMPLOYER},
    )
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "resume"], name="unique_saved_resume"),
        ]

    def __str__(self) -> str:
        return f"SavedResume<{self.user_id}: {self.resume_id}>"

