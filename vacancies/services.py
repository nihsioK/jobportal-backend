"""Service layer for vacancy business logic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from vacancies.models import Vacancy

if TYPE_CHECKING:
    from accounts.models import User

logger = logging.getLogger(__name__)


def create_vacancy(*, employer: User, data: dict[str, Any]) -> Vacancy:
    """Create a new vacancy owned by the given employer.

    Args:
        employer: The authenticated employer user.
        data: Validated vacancy field data.

    Returns:
        The persisted Vacancy instance.
    """
    logger.info("Creating vacancy for employer %s.", employer.email)
    vacancy = Vacancy(employer=employer, **data)
    vacancy.full_clean()
    vacancy.save()
    return vacancy
