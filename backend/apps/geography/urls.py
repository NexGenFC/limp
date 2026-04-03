from rest_framework.routers import DefaultRouter

from apps.geography.views import (
    DistrictViewSet,
    HobliViewSet,
    TalukViewSet,
    VillageViewSet,
)

router = DefaultRouter()
router.register("districts", DistrictViewSet, basename="district")
router.register("taluks", TalukViewSet, basename="taluk")
router.register("hoblis", HobliViewSet, basename="hobli")
router.register("villages", VillageViewSet, basename="village")

urlpatterns = router.urls
