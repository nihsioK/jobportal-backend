"""Management command to reindex all vacancies."""

from __future__ import annotations

import logging
from typing import Any

from django.core.management.base import BaseCommand

from search.indexing import format_vacancy, get_vacancy_index, init_index
from vacancies.models import Vacancy


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Reindexes all vacancies into MeiliSearch."""

    help = "Rebuilds the MeiliSearch index for vacancies."

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the reindex operation."""
        self.stdout.write("Fetching all vacancies...")
        vacancies = Vacancy.objects.all()
        count = vacancies.count()

        self.stdout.write("Formatting {count} vacancies...")
        docs = [format_vacancy(v) for v in vacancies]

        self.stdout.write("Updating MeiliSearch index...")
        init_index()
        index = get_vacancy_index()

        # Clear existing documents for a clean rebuild

        index.delete_all_documents()
        
        if docs:
            index.add_documents(docs)

        self.stdout.write(self.style.SUCCESS(f"Successfully reindexed {len(docs)} vacancies."))
