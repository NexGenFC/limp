from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.land.models import LandFile
from apps.land.serializers import LandFileMiniSerializer
from apps.legal.models import (
    CaseAdvocate,
    Hearing,
    LegalCase,
    PlanOfAction,
    POAStatus,
)

User = get_user_model()


class LegalCaseSerializer(serializers.ModelSerializer):
    """Land: nested mini on read; set ``land_uuid`` (FK UUID) on write."""

    land = LandFileMiniSerializer(read_only=True)
    land_id = serializers.CharField(source="land.land_id", read_only=True)
    land_uuid = serializers.PrimaryKeyRelatedField(
        queryset=LandFile.objects.all(),
        write_only=True,
        source="land",
    )
    advocates_count = serializers.SerializerMethodField()

    class Meta:
        model = LegalCase
        fields = (
            "id",
            "case_number",
            "title",
            "case_type",
            "court_jurisdiction",
            "party_role",
            "current_stage",
            "description",
            "land",
            "land_id",
            "land_uuid",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "advocates_count",
        )
        read_only_fields = (
            "id",
            "land_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def get_advocates_count(self, obj: LegalCase) -> int:
        return obj.case_advocates.filter(is_deleted=False).count()


class CaseAdvocateSerializer(serializers.ModelSerializer):
    case = serializers.PrimaryKeyRelatedField(queryset=LegalCase.objects.all())
    advocate = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    advocate_email = serializers.EmailField(
        source="advocate.email", read_only=True
    )

    class Meta:
        model = CaseAdvocate
        fields = (
            "id",
            "case",
            "advocate",
            "advocate_email",
            "role",
            "assigned_at",
            "created_at",
        )
        read_only_fields = ("id", "advocate_email", "assigned_at", "created_at")


class HearingSerializer(serializers.ModelSerializer):
    """
    Includes ``poa_status`` (via ``obj.poa``). When you add a ViewSet, use
    ``queryset.select_related("poa")`` on Hearing to avoid N+1 queries.
    """

    case = serializers.PrimaryKeyRelatedField(queryset=LegalCase.objects.all())
    land = serializers.PrimaryKeyRelatedField(queryset=LandFile.objects.all())
    poa_status = serializers.SerializerMethodField()

    class Meta:
        model = Hearing
        fields = (
            "id",
            "case",
            "land",
            "hearing_date",
            "stage_notes",
            "s3_key",
            "outcome",
            "poa_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "poa_status", "created_at", "updated_at")

    def get_poa_status(self, obj: Hearing):
        try:
            return obj.poa.status
        except PlanOfAction.DoesNotExist:
            return None


class PlanOfActionSerializer(serializers.ModelSerializer):
    hearing = serializers.PrimaryKeyRelatedField(queryset=Hearing.objects.all())
    land = serializers.PrimaryKeyRelatedField(queryset=LandFile.objects.all())

    class Meta:
        model = PlanOfAction
        fields = (
            "id",
            "hearing",
            "land",
            "status",
            "deadline",
            "submitted_at",
            "s3_key",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "deadline",
            "submitted_at",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        if (
            not request
            or request.method not in ("PATCH", "PUT")
            or self.instance is None
        ):
            return attrs

        if "status" in attrs and attrs["status"] != POAStatus.SUBMITTED:
            raise serializers.ValidationError(
                {
                    "status": "Only SUBMITTED is allowed when updating status.",
                }
            )

        status = attrs.get("status", self.instance.status)
        s3_key = attrs.get("s3_key", self.instance.s3_key)
        if status == POAStatus.SUBMITTED and (
            not s3_key or not str(s3_key).strip()
        ):
            raise serializers.ValidationError(
                {
                    "s3_key": "This field may not be blank when status is SUBMITTED.",
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data["status"] = POAStatus.PENDING
        return super().create(validated_data)
