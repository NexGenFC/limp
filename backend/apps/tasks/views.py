from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from apps.users.models import UserRole


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
