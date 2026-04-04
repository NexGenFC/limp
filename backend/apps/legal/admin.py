from django.contrib import admin

from apps.legal.models import LegalCase


@admin.register(LegalCase)
class LegalCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "land", "case_number", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    raw_id_fields = ("land", "created_by", "updated_by", "deleted_by")
