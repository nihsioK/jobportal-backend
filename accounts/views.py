"""Views for the accounts application."""

from __future__ import annotations

import logging
from typing import Any

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import Company, UserProfile, UserRole
from accounts.permissions import IsEmployer
from accounts.serializers import (
    CompanySerializer,
    RegisterSerializer,
    TokenPairResponseSerializer,
    TokenRefreshResponseSerializer,
    UserProfileSerializer,
    UserSerializer,
)


logger = logging.getLogger(__name__)


@extend_schema(
    tags=["accounts"],
    summary="Authenticate and issue JWTs",
    request=TokenObtainPairSerializer,
    responses={200: TokenPairResponseSerializer},
)
class LoginView(TokenObtainPairView):
    """Issue an access and refresh token pair for a valid user."""

    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=["accounts"],
    summary="Refresh an access token",
    request=TokenRefreshSerializer,
    responses={200: TokenRefreshResponseSerializer},
)
class RefreshView(TokenRefreshView):
    """Issue a fresh access token from a valid refresh token."""

    permission_classes = [permissions.AllowAny]


class RegisterView(APIView):
    """Create a user account."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="Register a new user",
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Register a new user and return its public payload."""
        logger.info("Received registration request.")
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Registration validation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        payload = UserSerializer(instance=user).data
        logger.info("Registration completed for user %s.", user.email)
        return Response(payload, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> UserProfile:
        """Return the profile for the authenticated user."""
        return self.request.user.profile


@extend_schema_view(
    list=extend_schema(summary="List companies", tags=["companies"]),
    retrieve=extend_schema(summary="Retrieve a company", tags=["companies"]),
    create=extend_schema(summary="Create a company profile", tags=["companies"]),
    partial_update=extend_schema(summary="Update your company", tags=["companies"]),
    destroy=extend_schema(summary="Delete your company", tags=["companies"]),
)
class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD API for companies."""

    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsEmployer()]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

    def get_queryset(self):
        if self.action in {"partial_update", "destroy"} and self.request.user.is_authenticated:
            return Company.objects.filter(employer=self.request.user)
        return super().get_queryset()


__all__ = ["LoginView", "RefreshView", "RegisterView", "ProfileView", "CompanyViewSet"]
