from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(response.data, dict) and response.data.get("success") is False:
        return response

    code = "ERROR"
    if response.status_code == status.HTTP_403_FORBIDDEN:
        code = "PERMISSION_DENIED"
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "UNAUTHENTICATED"
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"
    elif response.status_code == status.HTTP_400_BAD_REQUEST:
        code = "VALIDATION_ERROR"

    message = response.data
    if isinstance(message, dict) and "detail" in message:
        message = str(message["detail"])
    elif isinstance(message, list):
        message = "; ".join(str(m) for m in message)
    else:
        message = str(message)

    response.data = {
        "success": False,
        "error": {"code": code, "message": message},
    }
    return response
