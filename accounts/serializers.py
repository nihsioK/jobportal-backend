"""Serializers for the accounts application."""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import Company, UserProfile, UserRole, CompanyReview, CompanyFollower


logger = logging.getLogger(__name__)
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize extended user profile data."""

    class Meta:
        model = UserProfile
        fields = (
            "first_name",
            "last_name",
            "phone",
            "city",
            "birth_date",
            "avatar",
        )


class UserSerializer(serializers.ModelSerializer):
    """Serialize user payloads."""

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "role", "is_active", "created_at", "updated_at", "profile")
        read_only_fields = fields


class CompanySerializer(serializers.ModelSerializer):
    """Serialize company profiles."""

    class Meta:
        model = Company
        fields = (
            "id",
            "employer",
            "name",
            "description",
            "website",
            "logo",
            "industry",
            "city",
            "employee_count",
            "founded_year",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "employer", "created_at", "updated_at")


class CompanyReviewSerializer(serializers.ModelSerializer):
    """Serialize company reviews."""

    class Meta:
        model = CompanyReview
        fields = ("id", "company", "reviewer", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "reviewer", "created_at", "updated_at")


class CompanyFollowerSerializer(serializers.ModelSerializer):
    """Serialize company followers."""

    class Meta:
        model = CompanyFollower
        fields = ("id", "company", "follower", "created_at")
        read_only_fields = ("id", "follower", "created_at")



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

    def create(self, validated_data: dict[str, Any]) -> User:
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
