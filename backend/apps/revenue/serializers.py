from rest_framework import serializers
from .models import Officer, GovernmentWorkflow


class OfficerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Revenue Officer model (§3.1).
    Includes the human-readable designation for the frontend.
    """

    designation_display = serializers.CharField(
        source="get_designation_display", read_only=True
    )

    class Meta:
        model = Officer
        fields = [
            "id",
            "name",
            "designation",
            "designation_display",
            "district",
            "taluk",
            "internal_user",
        ]


class GovernmentWorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for the Government Workflow model (§3.2).
    Includes the computed 'days_pending' logic.
    """

    days_pending = serializers.ReadOnlyField()
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = GovernmentWorkflow
        fields = [
            "id",
            "land",
            "kind",
            "kind_display",
            "status",
            "status_display",
            "applied_on",
            "officer_handling",
            "days_pending",
            "remarks",
            "created_at",
            "updated_at",
        ]
