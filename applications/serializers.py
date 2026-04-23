"""Serializers for job applications."""

from __future__ import annotations

import logging
from typing import Any

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.request import Request

from applications.models import Application, ApplicationStatus, ApplicationStatusHistory
from resumes.models import Resume
from vacancies.models import Vacancy, VacancyStatus


logger = logging.getLogger(__name__)


class ApplicationListSerializer(serializers.ModelSerializer[Application]):
    """Read-only serializer for listing a seeker's applications."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    vacancy_employer = serializers.CharField(source="vacancy.employer.email", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "vacancy",
            "vacancy_title",
            "vacancy_employer",
            "status",
            "cover_letter",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """Serialize status history events."""

    changed_by = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = ("old_status", "new_status", "changed_by", "notes", "created_at")
        read_only_fields = fields


class ApplicationStatusSerializer(serializers.Serializer):
    """Serializer for employer-driven application status changes."""

    status = serializers.ChoiceField(
        choices=ApplicationStatus.choices,
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value: str) -> str:
        """Validate that the target status is a legal state."""
        logger.info("Validating status transition target: %s.", value)
        if value not in ApplicationStatus.values:
            raise serializers.ValidationError("Invalid status.")
        return value


def validate_request_resume(resume: Resume, request: Request) -> Resume:
    """Ensure the resume belongs to the authenticated user."""
    logger.info("Validating resume ownership.", extra={"user_id": getattr(request.user, "pk", None)})
    
    if resume.user != request.user:
        raise serializers.ValidationError("You do not own this resume.")
    return resume


class ApplicationSerializer(serializers.ModelSerializer[Application]):
    """Serializer for creating and reading applications."""

    vacancy = serializers.PrimaryKeyRelatedField(queryset=Vacancy.objects.select_related("employer").all())
    resume = serializers.PrimaryKeyRelatedField(queryset=Resume.objects.all())
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Application
        fields = ("id", "vacancy", "resume", "status", "cover_letter", "created_at", "updated_at")
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate application creation rules."""
        request = self.context.get("request")
        logger.info(
            "Validating application payload.",
            extra={"user_id": getattr(getattr(request, "user", None), "pk", None), "vacancy_id": getattr(attrs.get("vacancy"), "pk", None)},
        )

        if request is None:
            logger.error("Serializer context missing request object.")
            raise serializers.ValidationError("Request context is required.")

        resume = validate_request_resume(attrs["resume"], request)
        vacancy: Vacancy = attrs["vacancy"]

        if vacancy.status != VacancyStatus.OPEN:
            logger.error("Attempted application to a closed vacancy.", extra={"vacancy_id": vacancy.pk})
            raise serializers.ValidationError({"vacancy": "Applications are only allowed for open vacancies."})

        if Application.objects.filter(resume=resume, vacancy=vacancy).exists():
            logger.error(
                "Duplicate application attempt rejected.",
                extra={"resume_id": resume.pk, "vacancy_id": vacancy.pk},
            )
            raise serializers.ValidationError({"non_field_errors": ["You have already applied to this vacancy."]})

        attrs["resume"] = resume
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Application:
        """Create an application instance."""
        logger.info(
            "Creating application instance.",
            extra={"resume_id": validated_data["resume"].pk, "vacancy_id": validated_data["vacancy"].pk},
        )
        try:
            return Application.objects.create(**validated_data)
        except IntegrityError as exc:
            logger.error("Application creation hit a uniqueness constraint.", exc_info=exc)
            raise serializers.ValidationError({"non_field_errors": ["You have already applied to this vacancy."]}) from exc
