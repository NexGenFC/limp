from django.contrib import admin

from apps.legal.models import CaseAdvocate, Hearing, LegalCase, PlanOfAction


@admin.register(LegalCase)
class LegalCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "land", "case_number", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    raw_id_fields = ("land", "created_by", "updated_by", "deleted_by")


@admin.register(CaseAdvocate)
class CaseAdvocateAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "advocate", "role", "assigned_at", "is_deleted")
    list_filter = ("is_deleted",)
    raw_id_fields = ("case", "advocate", "created_by", "updated_by", "deleted_by")


@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "land", "hearing_date", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    raw_id_fields = ("case", "land", "created_by", "updated_by", "deleted_by")


@admin.register(PlanOfAction)
class PlanOfActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "hearing",
        "land",
        "deadline",
        "status",
        "created_at",
        "is_deleted",
    )
    list_filter = ("is_deleted", "status")
    raw_id_fields = ("hearing", "land", "created_by", "updated_by", "deleted_by")
