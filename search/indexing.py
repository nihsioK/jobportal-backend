"""Logic for indexing models into MeiliSearch."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings

from search.client import get_client

if TYPE_CHECKING:
    from vacancies.models import Vacancy

logger = logging.getLogger(__name__)


def get_vacancy_index() -> Any:
    """Get the vacancies index."""
    client = get_client()
    return client.index(settings.MEILI_VACANCY_INDEX)


def init_index() -> None:
    """Initialize and configure the MeiliSearch index."""
    logger.info("Initializing MeiliSearch index %s.", settings.MEILI_VACANCY_INDEX)
    index = get_vacancy_index()

    # Configure index settings
    index.update_searchable_attributes(["title", "description"])
    index.update_filterable_attributes(["status", "salary_min", "salary_max", "employer_id"])


def format_vacancy(vacancy: Vacancy) -> dict[str, Any]:
    """Format a Vacancy instance for MeiliSearch."""
    return {
        "id": vacancy.id,
        "title": vacancy.title,
        "description": vacancy.description,
        "salary_min": vacancy.salary_min,
        "salary_max": vacancy.salary_max,
        "status": vacancy.status,
        "employer_id": vacancy.employer_id,
        "created_at": vacancy.created_at.timestamp(),
        "updated_at": vacancy.updated_at.timestamp(),
    }


def upsert_vacancy(vacancy: Vacancy) -> None:
    """Upsert a vacancy into the MeiliSearch index."""
    logger.info("Upserting vacancy %s to MeiliSearch.", vacancy.id)
    index = get_vacancy_index()
    doc = format_vacancy(vacancy)
    index.add_documents([doc])


def delete_vacancy(vacancy_id: int) -> None:
    """Remove a vacancy from the MeiliSearch index."""
    logger.info("Deleting vacancy %s from MeiliSearch.", vacancy_id)
    index = get_vacancy_index()
    index.delete_document(str(vacancy_id))
