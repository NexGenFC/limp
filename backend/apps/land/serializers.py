from rest_framework import serializers

from apps.land.models import LandFile


class LandFileMiniSerializer(serializers.ModelSerializer):
    village_name = serializers.CharField(source="village.name", read_only=True)

    class Meta:
        model = LandFile
        fields = ("id", "land_id", "village_name")


class LandFileSerializer(serializers.ModelSerializer):
    village_name = serializers.CharField(source="village.name", read_only=True)
    hobli_name = serializers.CharField(source="village.hobli.name", read_only=True)
    taluk_name = serializers.CharField(
        source="village.hobli.taluk.name", read_only=True
    )
    district_name = serializers.CharField(
        source="village.hobli.taluk.district.name", read_only=True
    )

    class Meta:
        model = LandFile
        fields = (
            "id",
            "land_id",
            "village",
            "village_name",
            "hobli_name",
            "taluk_name",
            "district_name",
            "survey_number",
            "hissa",
            "extent_acres",
            "extent_guntas",
            "extent_sqft",
            "classification",
            "status",
            "proposed_by",
            "investment_min",
            "investment_max",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        read_only_fields = (
            "id",
            "land_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
