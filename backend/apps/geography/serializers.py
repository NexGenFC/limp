from rest_framework import serializers

from apps.geography.models import District, Hobli, Taluk, Village


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "name", "state")


class TalukSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = Taluk
        fields = ("id", "name", "district", "district_name")


class HobliSerializer(serializers.ModelSerializer):
    taluk_name = serializers.CharField(source="taluk.name", read_only=True)

    class Meta:
        model = Hobli
        fields = ("id", "name", "taluk", "taluk_name")


class VillageSerializer(serializers.ModelSerializer):
    hobli_name = serializers.CharField(source="hobli.name", read_only=True)

    class Meta:
        model = Village
        fields = ("id", "name", "hobli", "hobli_name")
