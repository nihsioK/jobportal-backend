"""Models for resume ownership and profile data."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Resume(models.Model):
    """Resume owned by a single job seeker."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resume",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    education = models.JSONField(default=list, blank=True)
    experience = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user_id"]

    def __str__(self) -> str:
        """Return the string representation of the resume."""
        return f"Resume<{self.user_id}>"
