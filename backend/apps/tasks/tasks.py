import logging
from datetime import date

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_task_assignment_notification(self, task_id: str) -> None:
    """Send assignment notification for a task (WhatsApp → SMS → stub)."""
    from apps.tasks.models import (
        NotificationChannel,
        NotificationLog,
        NotificationStatus,
        Task,
    )

    try:
        task = Task.all_objects.get(pk=task_id)
    except Task.DoesNotExist:
        logger.warning("Task %s not found — skipping notification", task_id)
        return

    # Idempotency: skip if already sent for this task
    if NotificationLog.all_objects.filter(
        task=task, status=NotificationStatus.SENT
    ).exists():
        return

    assignee = task.assigned_to
    phone = getattr(assignee, "phone", "") if assignee else ""
    message = f"New task assigned: {task.title}. Due: {task.due_date}"

    whatsapp_token = getattr(settings, "WHATSAPP_API_TOKEN", "") or ""
    if not whatsapp_token:
        NotificationLog.objects.create(
            task=task,
            channel=NotificationChannel.WHATSAPP,
            recipient_user=assignee,
            recipient_phone_e164=phone,
            status=NotificationStatus.STUB,
            message_summary=message,
        )
        return

    # Real send attempt
    try:
        _send_whatsapp(phone, message)
        NotificationLog.objects.create(
            task=task,
            channel=NotificationChannel.WHATSAPP,
            recipient_user=assignee,
            recipient_phone_e164=phone,
            status=NotificationStatus.SENT,
            message_summary=message,
        )
    except Exception as exc:  # noqa: BLE001
        NotificationLog.objects.create(
            task=task,
            channel=NotificationChannel.WHATSAPP,
            recipient_user=assignee,
            recipient_phone_e164=phone,
            status=NotificationStatus.FAILED,
            message_summary=message,
            error_detail=str(exc),
        )
        logger.exception("WhatsApp send failed for task %s", task_id)
        raise self.retry(exc=exc, countdown=60 * 15) from exc


def _send_whatsapp(phone: str, message: str) -> None:  # pragma: no cover
    """Call Meta WhatsApp Cloud API. Isolated for easy mocking."""
    import requests

    phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")
    token = getattr(settings, "WHATSAPP_API_TOKEN", "")
    requests.post(
        f"https://graph.facebook.com/v18.0/{phone_number_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message},
        },
        timeout=30,
    )


@shared_task(bind=True, max_retries=3)
def check_overdue_tasks(self) -> None:
    """Daily scan: flip overdue tasks and enqueue reminder notifications."""
    from apps.tasks.models import Task, TaskStatus

    overdue_qs = Task.objects.filter(
        due_date__lt=date.today(),
        is_deleted=False,
    ).exclude(
        status__in=[TaskStatus.DONE, TaskStatus.CANCELLED, TaskStatus.OVERDUE],
    )

    task_ids = list(overdue_qs.values_list("pk", flat=True))
    overdue_qs.update(status=TaskStatus.OVERDUE)

    for tid in task_ids:
        send_task_assignment_notification.delay(str(tid))
