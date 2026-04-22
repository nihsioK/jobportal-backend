"""Reusable DRF permission classes."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.models import UserRole


logger = logging.getLogger(__name__)


class IsEmployer(BasePermission):
    """Allow access only to authenticated employer users."""

    message = "Employer role required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the requester is an authenticated employer."""
        allowed = bool(request.user and request.user.is_authenticated and request.user.role == UserRole.EMPLOYER)
        logger.info("IsEmployer evaluated to %s for user %s.", allowed, getattr(request.user, "email", None))
        return allowed


class IsJobSeeker(BasePermission):
    """Allow access only to authenticated job seekers."""

    message = "Job seeker role required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the requester is an authenticated job seeker."""
        allowed = bool(request.user and request.user.is_authenticated and request.user.role == UserRole.JOB_SEEKER)
        logger.info("IsJobSeeker evaluated to %s for user %s.", allowed, getattr(request.user, "email", None))
        return allowed


class IsOwner(BasePermission):
    """Allow access only to the owner of the object."""

    message = "You do not own this resource."
    owner_field = "user"

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Ensure anonymous callers are rejected before object checks."""
        allowed = bool(request.user and request.user.is_authenticated)
        logger.info("IsOwner base permission evaluated to %s for user %s.", allowed, getattr(request.user, "email", None))
        return allowed

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Check object ownership using either the permission or view owner field."""
        if not request.user or not request.user.is_authenticated:
            logger.error("Anonymous user failed IsOwner object permission check.")
            return False

        owner_field = getattr(view, "owner_field", self.owner_field)
        owner = getattr(obj, owner_field, None)
        allowed = owner == request.user
        logger.info(
            "IsOwner object permission evaluated to %s using owner field %s for user %s.",
            allowed,
            owner_field,
            getattr(request.user, "email", None),
        )
        return allowed

