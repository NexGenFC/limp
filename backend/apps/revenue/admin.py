from django.contrib import admin

from apps.revenue.models import GovernmentWorkflow


@admin.register(GovernmentWorkflow)
class GovernmentWorkflowAdmin(admin.ModelAdmin):
    list_display = ("id", "land", "kind", "status", "applied_on", "is_deleted")
    list_filter = ("kind", "status", "is_deleted")
    raw_id_fields = ("land", "created_by", "updated_by", "deleted_by")
