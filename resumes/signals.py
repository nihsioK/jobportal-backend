"""Signal handlers for the resumes app."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, UserRole
from resumes.models import Resume


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_resume_for_job_seeker(
    sender: type[User],
    instance: User,
    created: bool,
    **kwargs: Any,
) -> None:
    """Ensure every job seeker has an attached resume."""
    logger.info(
        "Handling user post-save for resume provisioning.",
        extra={"email": instance.email, "user_created": created, "role": instance.role},
    )

    if not created or instance.role != UserRole.JOB_SEEKER:
        return

    Resume.objects.get_or_create(user=instance)
