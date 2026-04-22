"""Serializers for the accounts application."""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import UserRole

logger = logging.getLogger(__name__)
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serialize user payloads."""

    class Meta:
        model = User
        fields = ("id", "email", "role", "is_active", "created_at", "updated_at")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Handle user registration payloads."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password", "role", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "is_active", "created_at", "updated_at")

    def validate_role(self, value: str) -> str:
        """Validate the requested role."""
        logger.info("Validating registration role %s.", value)
        if value not in UserRole.values:
            logger.error("Registration received invalid role %s.", value)
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data: dict[str, Any]) -> "User":
        """Create a user from validated registration data."""
        logger.info("Creating a registered user with email %s.", validated_data.get("email"))
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class TokenPairResponseSerializer(serializers.Serializer):
    """Document the JWT login response payload."""

    access = serializers.CharField()
    refresh = serializers.CharField()


class TokenRefreshResponseSerializer(serializers.Serializer):
    """Document the JWT refresh response payload."""

    access = serializers.CharField()
