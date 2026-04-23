"""Views for self-service resume access."""

from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import UserRole
from accounts.permissions import IsJobSeeker, IsOwner

from .models import Resume
from .serializers import ResumeSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(summary="List your resumes", tags=["resumes"]),
    retrieve=extend_schema(summary="Retrieve a resume", tags=["resumes"]),
    create=extend_schema(summary="Create a resume", tags=["resumes"]),
    partial_update=extend_schema(summary="Update your resume", tags=["resumes"]),
    destroy=extend_schema(summary="Delete your resume", tags=["resumes"]),
)
class ResumeViewSet(viewsets.ModelViewSet):
    """CRUD API for job seeker resumes."""

    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker, IsOwner]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Resume.objects.none()
        return Resume.objects.filter(user=self.request.user).prefetch_related(
            "experience", "education", "languages", "certificates", "skills"
        )
