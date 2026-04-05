"""Register revenue / government workflow ViewSets when implementing Person 2 brief."""

from rest_framework.routers import DefaultRouter
from .views import OfficerViewSet, GovernmentWorkflowViewSet

# The Router automatically creates URLs like /officers/ and /workflows/
router = DefaultRouter()
router.register(r"officers", OfficerViewSet, basename="officer")
router.register(r"workflows", GovernmentWorkflowViewSet, basename="government-workflow")

urlpatterns = router.urls
