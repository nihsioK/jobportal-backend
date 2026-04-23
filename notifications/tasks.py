"""Celery tasks for the notifications application."""

from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="notifications.send_application_status_email",
)
def send_application_status_email(self, *, application_id: int) -> None:  # type: ignore[override]
    """Send an email notification when an application status changes.

    Args:
        application_id: Primary key of the updated Application.
    """
    from applications.models import Application

    logger.info(
        "Processing status-change email for application %s.", application_id
    )

    try:
        application = (
            Application.objects.select_related(
                "resume__user", "vacancy__employer"
            )
            .get(pk=application_id)
        )
    except Application.DoesNotExist:
        logger.error(
            "Application %s not found; skipping email.", application_id
        )
        return

    seeker = application.resume.user
    vacancy = application.vacancy
    status_display = application.get_status_display()

    subject = f"Application Update: {vacancy.title}"
    message = (
        f"Hello,\n\n"
        f"Your application for \"{vacancy.title}\" has been {status_display.lower()}.\n\n"
        f"Vacancy: {vacancy.title}\n"
        f"Employer: {vacancy.employer.email}\n"
        f"Status: {status_display}\n\n"
        f"Best regards,\n"
        f"JobPortal Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seeker.email],
            fail_silently=False,
        )
        logger.info(
            "Status-change email sent to %s for application %s.",
            seeker.email,
            application_id,
        )
    except Exception as exc:
        logger.error(
            "Failed to send status-change email for application %s: %s",
            application_id,
            exc,
        )
        raise self.retry(exc=exc)
