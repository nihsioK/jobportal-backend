"""URL patterns for resumes."""

from __future__ import annotations

from django.urls import path

from .views import ResumeMeAPIView

urlpatterns = [
    path("me/", ResumeMeAPIView.as_view(), name="resume-me"),
]
