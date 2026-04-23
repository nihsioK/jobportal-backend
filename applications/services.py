"""Service layer for application business logic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import transaction
from rest_framework.exceptions import ValidationError

from applications.models import Application, ApplicationStatus, ApplicationStatusHistory

if TYPE_CHECKING:
    from accounts.models import User

logger = logging.getLogger(__name__)

_VALID_TRANSITIONS: dict[str, set[str]] = {
    ApplicationStatus.PENDING: {ApplicationStatus.VIEWED, ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.VIEWED: {ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.INTERVIEW: {ApplicationStatus.OFFER, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.OFFER: {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.ACCEPTED: {ApplicationStatus.WITHDRAWN},
    ApplicationStatus.REJECTED: {ApplicationStatus.WITHDRAWN},
    ApplicationStatus.WITHDRAWN: set(),
}


def update_application_status(
    *,
    application: Application,
    new_status: str,
    user: User,
    notes: str = "",
) -> Application:
    """Transition an application to a new status.

    Validates ownership, transition legality, persists the history,
    and fires the async email notification.
    """
    vacancy = application.vacancy

    if new_status == ApplicationStatus.WITHDRAWN:
        if application.resume.user_id != user.pk:
            raise ValidationError({"detail": "Only the applicant can withdraw."})
    else:
        if vacancy.employer_id != user.pk:
            raise ValidationError({"detail": "You do not own this vacancy."})

    current = application.status
    if new_status not in _VALID_TRANSITIONS.get(current, set()):
        raise ValidationError(
            {"status": f"Cannot transition from {current} to {new_status}."}
        )

    with transaction.atomic():
        application.status = new_status
        application.save(update_fields=["status", "updated_at"])

        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=current,
            new_status=new_status,
            changed_by=user,
            notes=notes,
        )

    # Fire async email notification
    from notifications.tasks import send_application_status_email

    send_application_status_email.delay(application_id=application.pk)
    logger.info(
        "Dispatched status-change email task for application %s.",
        application.pk,
    )

    return application
