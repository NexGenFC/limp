from django.contrib import admin

from apps.tasks.models import NotificationLog, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "land",
        "status",
        "task_type",
        "due_date",
        "is_deleted",
    )
    list_filter = ("status", "task_type", "is_deleted")
    raw_id_fields = ("land", "assigned_to", "created_by", "updated_by", "deleted_by")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "channel", "status", "task", "created_at")
    list_filter = ("channel", "status")
    raw_id_fields = ("task", "recipient_user", "created_by", "updated_by", "deleted_by")
