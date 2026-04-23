"""URL configuration for the accounts application."""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from accounts.views import LoginView, RefreshView, RegisterView, ProfileView, CompanyViewSet

router = DefaultRouter()
router.register("companies", CompanyViewSet, basename="company")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", include(router.urls)),
]
