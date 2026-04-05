from rest_framework import viewsets
from .models import Officer, GovernmentWorkflow
from .serializers import OfficerSerializer, GovernmentWorkflowSerializer
from .permissions import IsRevenueTeamOrManagement


class OfficerViewSet(viewsets.ModelViewSet):
    serializer_class = OfficerSerializer
    permission_classes = [IsRevenueTeamOrManagement]

    def get_queryset(self):  # Fix 4: Use method, not class attribute
        return Officer.objects.filter(is_deleted=False)

    # Fix 3: Mandatory Audit & Soft Delete logic
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class GovernmentWorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = GovernmentWorkflowSerializer
    permission_classes = [IsRevenueTeamOrManagement]

    def get_queryset(self):  # Fix 4
        return GovernmentWorkflow.objects.filter(is_deleted=False).select_related(
            "land", "officer_handling"
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
