from rest_framework import viewsets
from .models import Officer, GovernmentWorkflow
from .serializers import OfficerSerializer, GovernmentWorkflowSerializer
from .permissions import IsRevenueTeamOrManagement


class OfficerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Revenue Officers (§3.1).
    Only returns active (is_deleted=False) officers.
    """

    queryset = Officer.objects.filter(is_deleted=False)
    serializer_class = OfficerSerializer
    permission_classes = [IsRevenueTeamOrManagement]


class GovernmentWorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Land Workflows (§3.3).
    Includes logic to filter out soft-deleted records.
    """

    serializer_class = GovernmentWorkflowSerializer
    permission_classes = [IsRevenueTeamOrManagement]

    def get_queryset(self):
        # Mandatory requirement §3.3: Explicitly filter is_deleted=False
        # select_related is used here to optimize the SQL query for linked data
        return GovernmentWorkflow.objects.filter(is_deleted=False).select_related(
            "land", "officer_handling"
        )
