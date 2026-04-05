from rest_framework import serializers

from apps.land.serializers import LandFileMiniSerializer
from apps.tasks.models import NotificationLog, Task


class TaskSerializer(serializers.ModelSerializer):
    land_detail = LandFileMiniSerializer(source="land", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "land",
            "land_detail",
            "title",
            "description",
            "task_type",
            "status",
            "due_date",
            "assigned_to",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = (
            "id",
            "task",
            "channel",
            "recipient_phone_e164",
            "recipient_user",
            "status",
            "message_summary",
            "error_detail",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
