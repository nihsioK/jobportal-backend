"""URL configuration for the search application."""

from django.urls import path

from search.views import VacancySearchView


app_name = "search"

urlpatterns = [
    path("vacancies/", VacancySearchView.as_view(), name="vacancy-search"),
]
