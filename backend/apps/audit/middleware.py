import json
import logging
from typing import Any

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _get_client_ip(request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _safe_body(request) -> dict[str, Any] | None:
    try:
        if request.content_type and "json" in request.content_type:
            return json.loads(request.body)
    except Exception:  # noqa: BLE001
        pass
    return None


class AuditMiddleware(MiddlewareMixin):
    """Log mutating API requests to AuditLog.

    When Kafka is configured, enqueue a Celery task to publish the row for
    Cassandra fan-out (see `apps.telemetry.tasks.publish_audit_log_event`).
    """

    def process_response(self, request, response):
        if request.method not in MUTATING_METHODS:
            return response
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return response
        if not request.path.startswith("/api/"):
            return response
        if response.status_code >= 400:
            return response

        action_map = {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }
        action = action_map.get(request.method, request.method)

        try:
            from apps.audit.models import AuditLog
            from apps.telemetry.tasks import publish_audit_log_event

            body = _safe_body(request)
            resp_data: dict[str, Any] | None = None
            try:
                resp_data = json.loads(response.content)
            except Exception:  # noqa: BLE001
                pass

            object_id = ""
            model_name = (
                request.resolver_match.url_name or "" if request.resolver_match else ""
            )

            if resp_data and isinstance(resp_data, dict):
                data = resp_data.get("data", resp_data)
                if isinstance(data, dict):
                    object_id = str(data.get("id", ""))

            log = AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=model_name,
                object_id=object_id,
                old_value=body if action in ("UPDATE", "DELETE") else None,
                new_value=resp_data if action in ("CREATE", "UPDATE") else None,
                ip_address=_get_client_ip(request),
            )
            publish_audit_log_event.delay(log.pk)
        except Exception:
            logger.exception("AuditMiddleware failed to log")

        return response
