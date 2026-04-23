"""Data models for job applications."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class ApplicationStatus(models.TextChoices):
    """Lifecycle states for an application."""

    PENDING = "PENDING", "Pending"
    VIEWED = "VIEWED", "Viewed"
    INTERVIEW = "INTERVIEW", "Interview"
    OFFER = "OFFER", "Offer"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class Application(models.Model):
    """Connect a resume to a vacancy."""

    resume = models.ForeignKey("resumes.Resume", related_name="applications", on_delete=models.CASCADE)
    vacancy = models.ForeignKey("vacancies.Vacancy", related_name="applications", on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    cover_letter = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("resume", "vacancy"), name="unique_resume_vacancy"),
        ]

    def __str__(self) -> str:
        return f"Application<{self.id}: {self.status}>"


class ApplicationStatusHistory(models.Model):
    """Track the history of status changes for an application."""

    application = models.ForeignKey(Application, related_name="status_history", on_delete=models.CASCADE)
    old_status = models.CharField(max_length=16, choices=ApplicationStatus.choices, blank=True, default="")
    new_status = models.CharField(max_length=16, choices=ApplicationStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"StatusChange<{self.application_id}: {self.old_status}->{self.new_status}>"

class Interview(models.Model):
    """Interview scheduled for an application."""
    application = models.ForeignKey(Application, related_name="interviews", on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, help_text="Zoom link or physical address")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self) -> str:
        return f"Interview<{self.id}: {self.application_id} @ {self.scheduled_at}>"


class ApplicationMessage(models.Model):
    """Direct message between employer and job seeker regarding an application."""
    application = models.ForeignKey(Application, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message<{self.id}: from {self.sender_id} on {self.application_id}>"
