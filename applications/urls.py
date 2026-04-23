"""URL routes for application APIs."""

from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from applications.views import (
    ApplicationStatusUpdateView,
    ApplicationViewSet,
    MyApplicationsView,
    InterviewViewSet,
    ApplicationMessageViewSet,
)


router = DefaultRouter()
router.register("", ApplicationViewSet, basename="application")
router.register("interviews", InterviewViewSet, basename="interview")
router.register("messages", ApplicationMessageViewSet, basename="message")

urlpatterns = [
    path("me/", MyApplicationsView.as_view(), name="application-me"),
    path(
        "<int:pk>/status/",
        ApplicationStatusUpdateView.as_view(),
        name="application-status-update",
    ),
    *router.urls,
]
