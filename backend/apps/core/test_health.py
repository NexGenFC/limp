import json

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_ok() -> None:
    client = APIClient()
    res = client.get("/api/v1/health/")
    assert res.status_code == 200
    payload = json.loads(res.content.decode("utf-8"))
    assert payload["success"] is True
    assert payload["data"]["status"] == "ok"


@pytest.mark.django_db
def test_login_envelope() -> None:
    from apps.users.models import User

    User.objects.create_user(email="u@u.com", password="pw12345678", role="FOUNDER")
    client = APIClient()
    res = client.post(
        "/api/v1/auth/login/",
        {"email": "u@u.com", "password": "pw12345678"},
        format="json",
    )
    assert res.status_code == 200
    payload = json.loads(res.content.decode("utf-8"))
    assert payload["success"] is True
    assert "access" in payload["data"]
    assert "refresh" in payload["data"]
