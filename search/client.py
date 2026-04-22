"""MeiliSearch client implementation."""

from __future__ import annotations

import logging
from typing import Any

import meilisearch
from django.conf import settings


logger = logging.getLogger(__name__)


class MeiliClient:
    """Singleton client for MeiliSearch operations."""

    _instance: meilisearch.Client | None = None

    def __new__(cls) -> meilisearch.Client:
        """Create or return the singleton MeiliSearch client instance."""
        if cls._instance is None:
            logger.info("Initializing MeiliSearch client at %s.", settings.MEILI_URL)
            cls._instance = meilisearch.Client(
                settings.MEILI_URL,
                settings.MEILI_MASTER_KEY,
            )
        return cls._instance


def get_client() -> meilisearch.Client:
    """Convenience function to get the MeiliSearch client."""
    return MeiliClient()
