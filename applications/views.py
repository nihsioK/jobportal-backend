"""Views for application management."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.permissions import IsEmployer, IsJobSeeker
from applications.models import Application
from applications.serializers import (
    ApplicationListSerializer,
    ApplicationSerializer,
    ApplicationStatusSerializer,
)
from applications.services import update_application_status


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


@extend_schema_view(
    get=extend_schema(
        tags=["applications"],
        summary="List your applications",
        responses={200: ApplicationListSerializer(many=True)},
    ),
)
class MyApplicationsView(generics.ListAPIView):
    """List all applications belonging to the authenticated job seeker."""

    serializer_class = ApplicationListSerializer
    permission_classes = (permissions.IsAuthenticated, IsJobSeeker)

    def get_queryset(self) -> QuerySet[Application]:
        """Return applications for the current user's resume."""
        user = self.request.user
        logger.info(
            "Listing applications for seeker.",
            extra={"email": getattr(user, "email", None)},
        )
        return (
            Application.objects
            .filter(resume__user=user)
            .select_related("vacancy", "vacancy__employer", "resume")
        )


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    """Allow an employer to accept or reject a candidate."""

    serializer_class = ApplicationStatusSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer)
    http_method_names = ["patch", "head", "options"]
    queryset = Application.objects.select_related(
        "resume__user", "vacancy__employer", "vacancy",
    )

    @extend_schema(
        tags=["applications"],
        summary="Update application status (accept / reject)",
        request=ApplicationStatusSerializer,
        responses={200: ApplicationListSerializer},
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Partially update the status of an application."""
        application = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger.info(
            "Employer %s updating application %s status to %s.",
            request.user.pk,
            application.pk,
            serializer.validated_data["status"],
        )

        updated = update_application_status(
            application=application,
            new_status=serializer.validated_data["status"],
            employer=request.user,
        )
        return Response(
            ApplicationListSerializer(updated).data,
            status=status.HTTP_200_OK,
        )
