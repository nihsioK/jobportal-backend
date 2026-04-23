"""Views for the accounts application."""

from __future__ import annotations

import logging
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.serializers import (
    RegisterSerializer,
    TokenPairResponseSerializer,
    TokenRefreshResponseSerializer,
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


__all__ = ["LoginView", "RefreshView", "RegisterView"]
