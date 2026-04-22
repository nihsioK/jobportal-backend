"""URL configuration for the vacancies application."""

from rest_framework.routers import DefaultRouter

from vacancies.views import VacancyViewSet

router = DefaultRouter()
router.register("", VacancyViewSet, basename="vacancy")

urlpatterns = router.urls
