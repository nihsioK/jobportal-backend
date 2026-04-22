"""Serializers for resume resources."""

from __future__ import annotations

import logging
from typing import Any, cast

from rest_framework import serializers

from .models import Resume

logger = logging.getLogger(__name__)


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for the authenticated user's resume."""

    class Meta:
        model = Resume
        fields = (
            "title",
            "summary",
            "education",
            "experience",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate_education(self, value: Any) -> list[dict[str, Any]]:
        """Validate the education JSON structure."""
        return self._validate_nested_list(field_name="education", value=value)

    def validate_experience(self, value: Any) -> list[dict[str, Any]]:
        """Validate the experience JSON structure."""
        return self._validate_nested_list(field_name="experience", value=value)

    @staticmethod
    def _validate_nested_list(*, field_name: str, value: Any) -> list[dict[str, Any]]:
        """Ensure JSON payloads are lists of objects with string keys."""
        logger.info("Validating nested JSON field", extra={"field_name": field_name})

        if not isinstance(value, list):
            logger.error(
                "Nested JSON validation failed because payload was not a list",
                extra={"field_name": field_name},
            )
            raise serializers.ValidationError("Expected a list of objects.")

        for index, item in enumerate(value):
            if not isinstance(item, dict):
                logger.error(
                    "Nested JSON validation failed because item was not an object",
                    extra={"field_name": field_name, "index": index},
                )
                raise serializers.ValidationError(
                    f"Item at index {index} must be an object."
                )

            if any(not isinstance(key, str) for key in item.keys()):
                logger.error(
                    "Nested JSON validation failed because a key was not a string",
                    extra={"field_name": field_name, "index": index},
                )
                raise serializers.ValidationError(
                    f"Item at index {index} must use string keys."
                )

        return cast(list[dict[str, Any]], value)
