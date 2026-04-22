"""URL configuration for the accounts application."""

from django.urls import path

from accounts.views import LoginView, RefreshView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
]
