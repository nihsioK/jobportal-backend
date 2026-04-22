"""Serializers for job applications."""

from __future__ import annotations

import logging
from typing import Any

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.request import Request

from applications.models import Application
from resumes.models import Resume
from vacancies.models import Vacancy, VacancyStatus

logger = logging.getLogger(__name__)


def get_request_resume(request: Request) -> Resume:
    """Resolve the authenticated user's resume."""
    logger.info("Resolving request resume.", extra={"user_id": getattr(request.user, "pk", None)})

    try:
        return request.user.resume # type: ignore
    except Resume.DoesNotExist as exc:
        logger.error("Authenticated user has no resume.", extra={"user_id": getattr(request.user, "pk", None)})
        raise serializers.ValidationError({"resume": "Authenticated job seeker does not have a resume."}) from exc


class ApplicationSerializer(serializers.ModelSerializer[Application]):
    """Serializer for creating and reading applications."""

    vacancy = serializers.PrimaryKeyRelatedField(queryset=Vacancy.objects.select_related("employer").all())
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Application
        fields = ("id", "vacancy", "status", "created_at", "updated_at")
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate application creation rules."""
        request = self.context.get("request")
        logger.info(
            "Validating application payload.",
            extra={
                "user_id": getattr(getattr(request, "user", None), "pk", None),
                "vacancy_id": getattr(attrs.get("vacancy"), "pk", None),
            },
        )

        if request is None:
            logger.error("Serializer context missing request object.")
            raise serializers.ValidationError("Request context is required.")

        resume = get_request_resume(request)
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
            raise serializers.ValidationError(
                {"non_field_errors": ["You have already applied to this vacancy."]}
            ) from exc
