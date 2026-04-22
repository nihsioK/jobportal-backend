"""Views for self-service resume access."""

from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import UserRole

from .models import Resume
from .serializers import ResumeSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(
        tags=["resumes"],
        summary="Retrieve your resume",
        responses={200: ResumeSerializer},
    ),
    patch=extend_schema(
        tags=["resumes"],
        summary="Update your resume",
        request=ResumeSerializer,
        responses={200: ResumeSerializer},
    ),
)
class ResumeMeAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve or partially update the authenticated seeker's resume."""

    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self) -> Resume:
        """Return the authenticated user's resume."""
        user = self.request.user

        if getattr(user, "role", None) != UserRole.JOB_SEEKER:
            logger.error(
                "Resume lookup rejected for non-job-seeker user",
                extra={"email": getattr(user, "email", None), "role": getattr(user, "role", None)},
            )
            raise NotFound("Resume not found.")

        try:
            resume = Resume.objects.select_related("user").get(user=user)
        except Resume.DoesNotExist as error:
            logger.error(
                "Resume lookup failed for authenticated job seeker",
                extra={"email": getattr(user, "email", None)},
            )
            raise NotFound("Resume not found.") from error

        logger.info(
            "Resolved resume for authenticated job seeker",
            extra={"email": getattr(user, "email", None)},
        )
        return resume

    def patch(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Partially update the authenticated user's resume."""
        logger.info(
            "PATCH request received for resume update",
            extra={"email": getattr(request.user, "email", None)},
        )
        return self.partial_update(request, *args, **kwargs)
