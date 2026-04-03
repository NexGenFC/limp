import json
import logging
import uuid
from datetime import datetime, timezone

from celery import shared_task
from django.conf import settings
from django.utils import timezone as dj_tz

logger = logging.getLogger(__name__)


def _kafka_servers() -> list[str]:
    raw = getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", "") or ""
    return [h.strip() for h in raw.split(",") if h.strip()]


@shared_task(bind=True, max_retries=3)
def publish_audit_log_event(self, audit_log_id: int) -> None:
    """Publish a compact audit payload to Kafka for Cassandra fan-out."""
    servers = _kafka_servers()
    if not servers:
        return

    try:
        from kafka import KafkaProducer
    except ImportError:
        logger.warning("kafka-python not installed")
        return

    try:
        from apps.audit.models import AuditLog

        log = AuditLog.objects.get(pk=audit_log_id)
    except AuditLog.DoesNotExist:
        return

    topic = getattr(settings, "KAFKA_AUDIT_TOPIC", "limp.audit")
    day = dj_tz.now().strftime("%Y-%m-%d")
    event_id = str(uuid.uuid1())
    payload = {
        "event_id": event_id,
        "django_audit_id": log.pk,
        "user_id": log.user_id,
        "action": log.action,
        "model_name": log.model_name,
        "object_id": log.object_id,
        "day": day,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {"old": log.old_value, "new": log.new_value},
    }

    try:
        producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            linger_ms=5,
        )
        producer.send(topic, value=payload)
        producer.flush(timeout=10)
        producer.close()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Kafka publish failed for audit %s", audit_log_id)
        raise self.retry(exc=exc, countdown=60) from exc
