from datetime import date, timedelta

from django.apps import apps
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.models import NotificationLog, Task
from apps.tasks.serializers import NotificationLogSerializer, TaskSerializer
from apps.users.models import UserRole
from apps.users.permissions import IsFounderOrManagement


_TASK_VIEW_ALL = frozenset({UserRole.FOUNDER, UserRole.MANAGEMENT})


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = Task.objects.select_related(
            "land__village__hobli__taluk__district",
            "assigned_to",
        ).filter(is_deleted=False)
        user = self.request.user
        if user.role not in _TASK_VIEW_ALL:
            qs = qs.filter(assigned_to=user)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        from apps.tasks.tasks import send_task_assignment_notification

        send_task_assignment_notification.delay(str(instance.id))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class DashboardStatsView(APIView):
    """Founder Command Center — aggregated stats across modules."""

    permission_classes = [IsFounderOrManagement]

    def get(self, request):
        today = date.today()

        # --- Land summary: count by status ---
        LandFile = apps.get_model("land", "LandFile")
        land_qs = LandFile.objects.filter(is_deleted=False)
        land_rows = land_qs.values("status").annotate(count=Count("id"))
        land_stats = {row["status"]: row["count"] for row in land_rows}

        # --- Task stats: overdue + due today ---
        task_qs = Task.objects.filter(is_deleted=False)
        overdue_total = task_qs.filter(status="OVERDUE").count()
        due_today = (
            task_qs.filter(due_date=today)
            .exclude(
                status__in=["DONE", "CANCELLED"],
            )
            .count()
        )
        task_stats = {"overdue_total": overdue_total, "due_today": due_today}

        # --- Legal preview: hearings in next 7 days ---
        legal_preview = _get_legal_preview(today)

        # --- Recent activity: last 10 notification logs ---
        recent_logs = NotificationLog.objects.order_by("-created_at")[:10]
        recent_activity = NotificationLogSerializer(recent_logs, many=True).data

        # --- Document health ---
        document_stats = _get_document_stats()

        return Response(
            {
                "land_stats": land_stats,
                "task_stats": task_stats,
                "legal_preview": legal_preview,
                "recent_activity": recent_activity,
                "document_stats": document_stats,
            }
        )


def _get_legal_preview(today: date) -> dict:
    """Count hearings in the next 7 days, or fall back to active legal cases."""
    try:
        Hearing = apps.get_model("legal", "Hearing")
        window = today + timedelta(days=7)
        count = Hearing.objects.filter(
            is_deleted=False,
            hearing_date__gte=today,
            hearing_date__lte=window,
        ).count()
        return {"hearings_next_7_days": count}
    except LookupError:
        # Hearing model not yet created by Person 1 — fall back to case count
        LegalCase = apps.get_model("legal", "LegalCase")
        count = LegalCase.objects.filter(is_deleted=False).count()
        return {"hearings_next_7_days": 0, "active_cases": count}


def _get_document_stats() -> dict:
    """Call Person 4's analytics service, or return placeholder if not ready."""
    try:
        from apps.documents.services import get_overall_completion_stats

        return get_overall_completion_stats()
    except ImportError:
        # Person 4 hasn't shipped the function yet — return safe default
        return {"avg_completion_percentage": 0.0}
