from typing import Any

from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    """Wrap successful responses in {success, data, meta} per LIMP API rules."""

    def render(
        self,
        data: Any,
        accepted_media_type: str | None,
        renderer_context: dict | None,
    ) -> bytes:
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        if response is not None and getattr(response, "exception", False):
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and data.get("success") is False:
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and "results" in data:
            meta = {k: v for k, v in data.items() if k != "results"}
            payload = {"success": True, "data": data["results"], "meta": meta}
        else:
            payload = {"success": True, "data": data, "meta": {}}

        return super().render(payload, accepted_media_type, renderer_context)
