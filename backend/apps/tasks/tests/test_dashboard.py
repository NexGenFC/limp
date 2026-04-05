import json
from datetime import date, timedelta

import pytest
from rest_framework.test import APIClient

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile, LandStatus
from apps.legal.models import LegalCase
from apps.tasks.models import (
    NotificationChannel,
    NotificationLog,
    NotificationStatus,
    Task,
    TaskStatus,
)
from apps.users.models import User, UserRole

DASHBOARD_URL = "/api/v1/dashboard/stats/"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def village(db):
    d = District.objects.create(name="Test District")
    t = Taluk.objects.create(name="Test Taluk", district=d)
    h = Hobli.objects.create(name="Test Hobli", taluk=t)
    return Village.objects.create(name="Test Village", hobli=h)


def _make_user(role, suffix=""):
    return User.objects.create_user(
        email=f"{role.lower()}{suffix}@test.com",
        password="pw12345678",
        role=role,
    )


def _auth(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def founder(db):
    return _make_user(UserRole.FOUNDER)


@pytest.fixture
def management(db):
    return _make_user(UserRole.MANAGEMENT)


@pytest.fixture
def field_staff(db):
    return _make_user(UserRole.FIELD_STAFF)


@pytest.fixture
def advocate(db):
    return _make_user(UserRole.IN_HOUSE_ADVOCATE)


@pytest.fixture
def land(village, founder):
    return LandFile.objects.create(
        village=village,
        survey_number="1",
        status=LandStatus.ACTIVE,
        created_by=founder,
        updated_by=founder,
    )


# ---------------------------------------------------------------------------
# RBAC
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_founder_can_access_dashboard(founder):
    res = _auth(founder).get(DASHBOARD_URL)
    assert res.status_code == 200


@pytest.mark.django_db
def test_management_can_access_dashboard(management):
    res = _auth(management).get(DASHBOARD_URL)
    assert res.status_code == 200


@pytest.mark.django_db
def test_field_staff_forbidden(field_staff):
    res = _auth(field_staff).get(DASHBOARD_URL)
    assert res.status_code == 403


@pytest.mark.django_db
def test_advocate_forbidden(advocate):
    res = _auth(advocate).get(DASHBOARD_URL)
    assert res.status_code == 403


@pytest.mark.django_db
def test_unauthenticated_denied():
    res = APIClient().get(DASHBOARD_URL)
    assert res.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Response structure
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_response_has_required_keys(founder):
    res = _auth(founder).get(DASHBOARD_URL)
    body = json.loads(res.content)
    assert body["success"] is True
    data = body["data"]
    assert "land_stats" in data
    assert "task_stats" in data
    assert "legal_preview" in data
    assert "recent_activity" in data
    assert "document_stats" in data


# ---------------------------------------------------------------------------
# Aggregation correctness
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_land_stats_counts(founder, village):
    for _ in range(3):
        LandFile.objects.create(
            village=village,
            survey_number="x",
            status=LandStatus.ACTIVE,
            created_by=founder,
            updated_by=founder,
        )
    LandFile.objects.create(
        village=village,
        survey_number="y",
        status=LandStatus.CLOSED,
        created_by=founder,
        updated_by=founder,
    )

    res = _auth(founder).get(DASHBOARD_URL)
    data = json.loads(res.content)["data"]
    assert data["land_stats"].get("ACTIVE", 0) == 3
    assert data["land_stats"].get("CLOSED", 0) == 1


@pytest.mark.django_db
def test_task_stats(land, founder):
    Task.objects.create(
        land=land,
        title="Overdue",
        assigned_to=founder,
        status=TaskStatus.OVERDUE,
    )
    Task.objects.create(
        land=land,
        title="Due today",
        assigned_to=founder,
        status=TaskStatus.OPEN,
        due_date=date.today(),
    )
    Task.objects.create(
        land=land,
        title="Future",
        assigned_to=founder,
        status=TaskStatus.OPEN,
        due_date=date.today() + timedelta(days=5),
    )

    res = _auth(founder).get(DASHBOARD_URL)
    data = json.loads(res.content)["data"]
    assert data["task_stats"]["overdue_total"] == 1
    assert data["task_stats"]["due_today"] == 1


@pytest.mark.django_db
def test_legal_preview_without_hearing_model(land, founder):
    """While Hearing hasn't been built, we get hearings_next_7_days = 0."""
    LegalCase.objects.create(land=land, case_number="CC-001")

    res = _auth(founder).get(DASHBOARD_URL)
    data = json.loads(res.content)["data"]
    assert data["legal_preview"]["hearings_next_7_days"] == 0
    # Fallback provides active_cases when Hearing doesn't exist
    assert data["legal_preview"].get("active_cases", 0) >= 1


@pytest.mark.django_db
def test_recent_activity(land, founder):
    task = Task.objects.create(land=land, title="T", assigned_to=founder)
    for i in range(12):
        NotificationLog.objects.create(
            task=task,
            channel=NotificationChannel.INTERNAL,
            status=NotificationStatus.STUB,
            message_summary=f"msg-{i}",
        )

    res = _auth(founder).get(DASHBOARD_URL)
    data = json.loads(res.content)["data"]
    assert len(data["recent_activity"]) == 10  # capped at 10


@pytest.mark.django_db
def test_document_stats_default(founder):
    """Without Person 4's service, default avg_completion_percentage is 0.0."""
    res = _auth(founder).get(DASHBOARD_URL)
    data = json.loads(res.content)["data"]
    assert "avg_completion_percentage" in data["document_stats"]
