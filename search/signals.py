"""Signals for indexing models into MeiliSearch."""

from __future__ import annotations

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from meilisearch.errors import MeilisearchCommunicationError

from search.indexing import delete_vacancy, upsert_vacancy
from vacancies.models import Vacancy


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Vacancy)
def vacancy_post_save(sender: type[Vacancy], instance: Vacancy, **kwargs: object) -> None:
    """Trigger indexing of a vacancy after save."""
    logger.info("Signal: post_save for Vacancy %s.", instance.id)
    try:
        upsert_vacancy(instance)
    except MeilisearchCommunicationError:
        logger.error("MeiliSearch unavailable; skipping indexing for Vacancy %s.", instance.id)


@receiver(post_delete, sender=Vacancy)
def vacancy_post_delete(sender: type[Vacancy], instance: Vacancy, **kwargs: object) -> None:
    """Remove vacancy from index after deletion."""
    logger.info("Signal: post_delete for Vacancy %s.", instance.id)
    try:
        delete_vacancy(instance.id)
    except MeilisearchCommunicationError:
        logger.error("MeiliSearch unavailable; skipping deletion for Vacancy %s.", instance.id)
