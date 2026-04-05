from rest_framework.routers import DefaultRouter

from apps.legal.views import (
    CaseAdvocateViewSet,
    HearingViewSet,
    LegalCaseViewSet,
    PlanOfActionViewSet,
)

router = DefaultRouter()
router.register("legal/cases", LegalCaseViewSet, basename="legal-case")
router.register("legal/hearings", HearingViewSet, basename="legal-hearing")
router.register("legal/poa", PlanOfActionViewSet, basename="legal-poa")
router.register(
    "legal/case-advocates",
    CaseAdvocateViewSet,
    basename="legal-case-advocate",
)

urlpatterns = router.urls
