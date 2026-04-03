from rest_framework.routers import DefaultRouter

from apps.land.views import LandFileViewSet

router = DefaultRouter()
router.register("land", LandFileViewSet, basename="land")

urlpatterns = router.urls
