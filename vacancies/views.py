"""Views for the vacancies application."""

from __future__ import annotations

import logging
from typing import Any, cast

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from django.db.models import QuerySet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsEmployer, IsOwner
from applications.models import Application
from applications.serializers import ApplicationListSerializer
from vacancies.models import Vacancy
from vacancies.serializers import VacancySerializer


logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=["vacancies"],
        summary="List vacancies",
        parameters=[
            OpenApiParameter(name="status", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="employer", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="salary_min", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="salary_max", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        ],
        responses={200: VacancySerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["vacancies"],
        summary="Retrieve a vacancy",
        responses={200: VacancySerializer},
    ),
    create=extend_schema(
        tags=["vacancies"],
        summary="Create a vacancy",
        request=VacancySerializer,
        responses={201: VacancySerializer},
    ),
    partial_update=extend_schema(
        tags=["vacancies"],
        summary="Update your vacancy",
        request=VacancySerializer,
        responses={200: VacancySerializer},
    ),
    destroy=extend_schema(
        tags=["vacancies"],
        summary="Delete your vacancy",
        responses={204: None},
    ),
    mine=extend_schema(
        tags=["vacancies"],
        summary="List your vacancies",
        responses={200: VacancySerializer(many=True)},
    ),
    applicants=extend_schema(
        tags=["vacancies"],
        summary="List applicants for your vacancy",
        responses={200: ApplicationListSerializer(many=True)},
    ),
)
class VacancyViewSet(viewsets.ModelViewSet):
    """CRUD API for vacancies with public read access."""

    serializer_class = VacancySerializer
    queryset = Vacancy.objects.select_related("employer")
    owner_field = "employer"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self) -> list[permissions.BasePermission]:
        """Resolve permissions per action."""
        logger.info("Resolving permissions for vacancy action %s.", self.action)
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        if self.action in {"mine", "create"}:
            return [permissions.IsAuthenticated(), IsEmployer()]
        if self.action == "applicants":
            return [permissions.IsAuthenticated(), IsEmployer(), IsOwner()]
        return [permissions.IsAuthenticated(), IsEmployer(), IsOwner()]

    def get_queryset(self) -> QuerySet[Vacancy]:
        """Return the queryset for the current action and filters."""
        logger.info("Building queryset for vacancy action %s.", self.action)
        queryset = cast(QuerySet[Vacancy], super().get_queryset().select_related("employer"))
        request = self.request

        if self.action == "mine" and request.user.is_authenticated:
            logger.info("Restricting vacancies to employer %s.", getattr(request.user, "email", None))
            queryset = queryset.filter(employer=request.user)

        status_value = request.query_params.get("status")
        if status_value:
            logger.info("Applying vacancy status filter %s.", status_value)
            queryset = queryset.filter(status=status_value)

        employer_email = request.query_params.get("employer")
        if employer_email:
            logger.info("Applying employer filter %s.", employer_email)
            queryset = queryset.filter(employer__email=employer_email)

        minimum_salary = request.query_params.get("salary_min")
        if minimum_salary:
            logger.info("Applying salary_min filter %s.", minimum_salary)
            queryset = queryset.filter(salary_min__gte=minimum_salary)

        maximum_salary = request.query_params.get("salary_max")
        if maximum_salary:
            logger.info("Applying salary_max filter %s.", maximum_salary)
            queryset = queryset.filter(salary_max__lte=maximum_salary)

        return queryset

    def perform_create(self, serializer: VacancySerializer) -> None:
        """Create a vacancy owned by the authenticated employer."""
        employer = cast(User, self.request.user)
        logger.info("Creating vacancy for employer %s.", employer.email)
        serializer.save(employer=employer)

    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return vacancies owned by the authenticated employer."""
        logger.info("Listing own vacancies for employer %s.", getattr(request.user, "email", None))
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="applicants")
    def applicants(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return all applications for the given vacancy."""
        vacancy = self.get_object()
        logger.info(
            "Listing applicants for vacancy %s (employer %s).",
            vacancy.pk,
            getattr(request.user, "email", None),
        )
        applications = (
            Application.objects
            .filter(vacancy=vacancy)
            .select_related("resume__user", "vacancy", "vacancy__employer")
        )
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = ApplicationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ApplicationListSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
