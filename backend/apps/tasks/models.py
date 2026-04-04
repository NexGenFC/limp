"""
Tasks & notification log — land-anchored workflow (PRD §12, HLD §3.4, §6).

Person 3 adds Celery tasks, WhatsApp/SMS integration, queryset scoping, and APIs.
"""

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class TaskStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    DONE = "DONE", "Done"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"


class TaskType(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    LEGAL_POA = "LEGAL_POA", "Legal — plan of action"
    REVENUE_FOLLOWUP = "REVENUE_FOLLOWUP", "Revenue follow-up"
    SURVEY = "SURVEY", "Survey"
    OTHER = "OTHER", "Other"


class Task(BaseModel):
    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(
        max_length=64,
        choices=TaskType.choices,
        default=TaskType.MANUAL,
    )
    status = models.CharField(
        max_length=32,
        choices=TaskStatus.choices,
        default=TaskStatus.OPEN,
    )
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self) -> str:
        return f"{self.title} ({self.land.land_id})"


class NotificationChannel(models.TextChoices):
    WHATSAPP = "WHATSAPP", "WhatsApp"
    SMS = "SMS", "SMS"
    INTERNAL = "INTERNAL", "Internal log"


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    STUB = "STUB", "Stub (dev / not configured)"


class NotificationLog(BaseModel):
    """
    Append-only style usage in application code; rows are never hard-deleted.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notification_logs",
    )
    channel = models.CharField(max_length=32, choices=NotificationChannel.choices)
    recipient_phone_e164 = models.CharField(
        max_length=20,
        blank=True,
        help_text="E.164, e.g. +9198XXXXX per docs/rules.md",
    )
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_logs_received",
    )
    status = models.CharField(
        max_length=32,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    message_summary = models.CharField(max_length=512, blank=True)
    error_detail = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification log"
        verbose_name_plural = "Notification logs"

    def __str__(self) -> str:
        return f"{self.channel} {self.status} #{self.pk}"
