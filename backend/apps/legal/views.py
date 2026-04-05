from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.legal.models import (
    CaseAdvocate,
    Hearing,
    LegalCase,
    PlanOfAction,
    POAStatus,
)
from apps.legal.serializers import (
    CaseAdvocateSerializer,
    HearingSerializer,
    LegalCaseSerializer,
    PlanOfActionSerializer,
)
from apps.users.models import UserRole
from apps.users.permissions import (
    CanViewLegalCases,
    IsFounderOrManagement,
    IsInHouseAdvocateOrAbove,
)


class LegalCaseViewSet(viewsets.ModelViewSet):
    serializer_class = LegalCaseSerializer
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), CanViewLegalCases()]
        if self.action in ("create", "update", "partial_update"):
            return [IsAuthenticated(), IsInHouseAdvocateOrAbove()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsFounderOrManagement()]
        return [IsAuthenticated(), CanViewLegalCases()]

    def get_queryset(self):
        qs = (
            LegalCase.objects.select_related("land__village")
            .prefetch_related("case_advocates__advocate")
        )
        user = self.request.user
        if user.is_authenticated and user.role == UserRole.EXTERNAL_ADVOCATE:
            return qs.filter(assigned_advocates=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class CaseAdvocateViewSet(viewsets.ModelViewSet):
    serializer_class = CaseAdvocateSerializer
    permission_classes = [IsAuthenticated, IsInHouseAdvocateOrAbove]
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        qs = CaseAdvocate.objects.select_related("case", "advocate")
        case_id = self.request.query_params.get("case")
        if case_id:
            qs = qs.filter(case_id=case_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class HearingViewSet(viewsets.ModelViewSet):
    serializer_class = HearingSerializer
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), CanViewLegalCases()]
        if self.action in ("create", "update", "partial_update"):
            return [IsAuthenticated(), IsInHouseAdvocateOrAbove()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsFounderOrManagement()]
        return [IsAuthenticated(), CanViewLegalCases()]

    def get_queryset(self):
        qs = Hearing.objects.select_related("case", "land", "poa")
        case_id = self.request.query_params.get("case")
        if case_id:
            qs = qs.filter(case_id=case_id)
        user = self.request.user
        if user.is_authenticated and user.role == UserRole.EXTERNAL_ADVOCATE:
            qs = qs.filter(case__assigned_advocates=user)
        return qs

    def perform_create(self, serializer):
        case = serializer.validated_data["case"]
        serializer.save(
            land=case.land,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class PlanOfActionViewSet(viewsets.ModelViewSet):
    serializer_class = PlanOfActionSerializer
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), CanViewLegalCases()]
        if self.action in ("create", "update", "partial_update"):
            return [IsAuthenticated(), IsInHouseAdvocateOrAbove()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsFounderOrManagement()]
        return [IsAuthenticated(), CanViewLegalCases()]

    def get_queryset(self):
        qs = PlanOfAction.objects.select_related(
            "hearing",
            "hearing__case",
            "land",
        )
        user = self.request.user
        if user.is_authenticated and user.role == UserRole.EXTERNAL_ADVOCATE:
            qs = qs.filter(hearing__case__assigned_advocates=user)
        return qs

    def perform_create(self, serializer):
        hearing = serializer.validated_data["hearing"]
        serializer.save(
            land=hearing.case.land,
            deadline=PlanOfAction.compute_deadline(hearing.hearing_date),
            status=POAStatus.PENDING,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        kwargs = {"updated_by": self.request.user}
        new_status = serializer.validated_data.get("status", instance.status)
        if (
            new_status == POAStatus.SUBMITTED
            and instance.status != POAStatus.SUBMITTED
        ):
            kwargs["submitted_at"] = timezone.now()
        serializer.save(**kwargs)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
