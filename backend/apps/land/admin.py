from django.contrib import admin

from apps.land.models import LandFile


@admin.register(LandFile)
class LandFileAdmin(admin.ModelAdmin):
    list_display = (
        "land_id",
        "village",
        "survey_number",
        "classification",
        "status",
        "created_at",
    )
    list_filter = ("classification", "status", "village__hobli__taluk__district")
    search_fields = ("land_id", "survey_number")
    readonly_fields = (
        "land_id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
