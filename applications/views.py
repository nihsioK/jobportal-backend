"""Views for application management."""

from __future__ import annotations

import logging

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.permissions import IsJobSeeker
from applications.models import Application
from applications.serializers import ApplicationSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    create=extend_schema(
        tags=["applications"],
        summary="Create a job application",
        request=ApplicationSerializer,
        responses={201: ApplicationSerializer},
    ),
)
class ApplicationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Create job applications for the authenticated job seeker."""

    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsJobSeeker)
    http_method_names = ["post", "head", "options"]

    def get_queryset(self) -> QuerySet[Application]:
        """Return the optimized application queryset."""
        logger.info("Building application queryset.")
        return Application.objects.select_related("resume", "vacancy", "vacancy__employer")

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Create a new application for the authenticated job seeker."""
        logger.info("Received application create request.", extra={"user_id": getattr(request.user, "pk", None)})
        return super().create(request, *args, **kwargs)
