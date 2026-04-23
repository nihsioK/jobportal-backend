"""Service layer for application business logic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import transaction
from rest_framework.exceptions import ValidationError

from applications.models import Application, ApplicationStatus

if TYPE_CHECKING:
    from accounts.models import User

logger = logging.getLogger(__name__)

_VALID_TRANSITIONS: dict[str, set[str]] = {
    ApplicationStatus.PENDING: {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED},
    ApplicationStatus.ACCEPTED: set(),
    ApplicationStatus.REJECTED: set(),
}


def update_application_status(
    *,
    application: Application,
    new_status: str,
    employer: User,
) -> Application:
    """Transition an application to a new status.

    Validates ownership, transition legality, then persists and fires
    the async email notification.

    Args:
        application: The application instance to update.
        new_status: Target status value (ACCEPTED / REJECTED).
        employer: The authenticated employer performing the action.

    Returns:
        The updated application instance.

    Raises:
        ValidationError: If the transition is invalid or the employer
            does not own the vacancy.
    """
    vacancy = application.vacancy

    if vacancy.employer_id != employer.pk:
        logger.error(
            "Employer %s attempted status change on application %s they do not own.",
            employer.pk,
            application.pk,
        )
        raise ValidationError({"detail": "You do not own this vacancy."})

    current = application.status
    if new_status not in _VALID_TRANSITIONS.get(current, set()):
        logger.error(
            "Invalid status transition %s -> %s for application %s.",
            current,
            new_status,
            application.pk,
        )
        raise ValidationError(
            {"status": f"Cannot transition from {current} to {new_status}."}
        )

    logger.info(
        "Transitioning application %s from %s to %s.",
        application.pk,
        current,
        new_status,
    )

    with transaction.atomic():
        application.status = new_status
        application.save(update_fields=["status", "updated_at"])

    # Fire async email notification
    from notifications.tasks import send_application_status_email

    send_application_status_email.delay(application_id=application.pk)
    logger.info(
        "Dispatched status-change email task for application %s.",
        application.pk,
    )

    return application
