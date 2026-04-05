from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.tasks.views import DashboardStatsView, TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    *router.urls,
]
