"""Serializers for the vacancies application."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework import serializers

from vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class VacancySerializer(serializers.ModelSerializer[Vacancy]):
    """Serialize vacancy payloads."""

    employer: Any = serializers.SlugRelatedField(read_only=True, slug_field="email")

    class Meta:
        model = Vacancy
        fields = (
            "id",
            "employer",
            "title",
            "description",
            "salary_min",
            "salary_max",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "employer", "created_at", "updated_at")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Run model-level salary validation before persistence."""
        logger.info("Validating vacancy payload.")
        instance = getattr(self, "instance", None)
        employer = getattr(instance, "employer", None) or getattr(self.context.get("request"), "user", None)
        salary_min = attrs.get("salary_min", getattr(instance, "salary_min", None))
        salary_max = attrs.get("salary_max", getattr(instance, "salary_max", None))
        title = attrs.get("title", getattr(instance, "title", ""))
        description = attrs.get("description", getattr(instance, "description", ""))
        status = attrs.get("status", getattr(instance, "status", None))

        candidate = Vacancy(
            employer=employer,
            title=title,
            description=description,
            salary_min=salary_min,
            salary_max=salary_max,
            status=status,
        )

        try:
            candidate.clean()
        except Exception as exc:  # noqa: BLE001
            logger.error("Vacancy serializer validation failed: %s", exc)
            raise serializers.ValidationError(getattr(exc, "message_dict", {"detail": str(exc)})) from exc

        return attrs
