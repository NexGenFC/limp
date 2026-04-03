from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.geography.models import District, Hobli, Taluk, Village
from apps.geography.serializers import (
    DistrictSerializer,
    HobliSerializer,
    TalukSerializer,
    VillageSerializer,
)


class DistrictViewSet(ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]


class TalukViewSet(ReadOnlyModelViewSet):
    serializer_class = TalukSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Taluk.objects.select_related("district")
        district_id = self.request.query_params.get("district")
        if district_id:
            qs = qs.filter(district_id=district_id)
        return qs


class HobliViewSet(ReadOnlyModelViewSet):
    serializer_class = HobliSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Hobli.objects.select_related("taluk")
        taluk_id = self.request.query_params.get("taluk")
        if taluk_id:
            qs = qs.filter(taluk_id=taluk_id)
        return qs


class VillageViewSet(ReadOnlyModelViewSet):
    serializer_class = VillageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Village.objects.select_related("hobli")
        hobli_id = self.request.query_params.get("hobli")
        if hobli_id:
            qs = qs.filter(hobli_id=hobli_id)
        return qs
