from rest_framework import viewsets

from apps.land.models import LandFile
from apps.land.serializers import LandFileSerializer
from apps.users.permissions import LandPermission


class LandFileViewSet(viewsets.ModelViewSet):
    serializer_class = LandFileSerializer
    permission_classes = [LandPermission]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return LandFile.objects.select_related("village__hobli__taluk__district").all()

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
