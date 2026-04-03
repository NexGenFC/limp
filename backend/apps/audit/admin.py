from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action",
        "model_name",
        "object_id",
        "ip_address",
    )
    list_filter = ("action", "model_name")
    search_fields = ("model_name", "object_id")
    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "old_value",
        "new_value",
        "ip_address",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
