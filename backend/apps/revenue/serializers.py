from rest_framework import serializers
from .models import Officer, GovernmentWorkflow


class OfficerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Revenue Officer model.
    Includes designation display and audit fields for the LIMP standard.
    """

    designation_display = serializers.CharField(
        source="get_designation_display", read_only=True
    )

    class Meta:
        model = Officer
        # Fix Minor 4 & 5: Use tuples and consistent naming
        fields = (
            "id",
            "name",
            "designation",
            "designation_display",
            "district",
            "taluk",
            "internal_user",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",  # Fix 9: Added audit fields
        )
        # Fix 9: Define read-only fields strictly
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


class GovernmentWorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for the Government Workflow model.
    Exposes the computed days_pending logic and audit trail.
    """

    days_pending = serializers.ReadOnlyField()
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = GovernmentWorkflow
        # Fix 9: Added audit fields and used tuples for project consistency
        fields = (
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
            "created_by",
            "updated_by",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
