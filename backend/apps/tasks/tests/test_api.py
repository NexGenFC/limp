import json

import pytest
from rest_framework.test import APIClient

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile
from apps.tasks.models import Task
from apps.users.models import User, UserRole

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
def field_staff_a(db):
    return _make_user(UserRole.FIELD_STAFF, suffix="-a")


@pytest.fixture
def field_staff_b(db):
    return _make_user(UserRole.FIELD_STAFF, suffix="-b")


@pytest.fixture
def land(village, founder):
    return LandFile.objects.create(
        village=village,
        survey_number="1",
        created_by=founder,
        updated_by=founder,
    )


TASK_ENDPOINT = "/api/v1/tasks/"


# ---------------------------------------------------------------------------
# Queryset scoping
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_field_staff_sees_only_own_tasks(land, field_staff_a, field_staff_b):
    Task.objects.create(land=land, title="Task A", assigned_to=field_staff_a)
    Task.objects.create(land=land, title="Task B", assigned_to=field_staff_b)

    res = _auth(field_staff_a).get(TASK_ENDPOINT)
    body = json.loads(res.content)
    assert res.status_code == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["title"] == "Task A"


@pytest.mark.django_db
def test_field_staff_cannot_see_others_tasks(land, field_staff_a, field_staff_b):
    task_b = Task.objects.create(land=land, title="Task B", assigned_to=field_staff_b)

    res = _auth(field_staff_a).get(f"{TASK_ENDPOINT}{task_b.pk}/")
    assert res.status_code == 404


@pytest.mark.django_db
def test_founder_sees_all_tasks(land, founder, field_staff_a, field_staff_b):
    Task.objects.create(land=land, title="Task A", assigned_to=field_staff_a)
    Task.objects.create(land=land, title="Task B", assigned_to=field_staff_b)

    res = _auth(founder).get(TASK_ENDPOINT)
    body = json.loads(res.content)
    assert res.status_code == 200
    assert len(body["data"]) == 2


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_task(land, founder):
    payload = {
        "land": str(land.pk),
        "title": "New task",
        "description": "Some work",
        "task_type": "MANUAL",
        "assigned_to": founder.pk,
    }
    res = _auth(founder).post(TASK_ENDPOINT, payload, format="json")
    body = json.loads(res.content)
    assert res.status_code == 201
    assert body["success"] is True
    assert body["data"]["title"] == "New task"


@pytest.mark.django_db
def test_soft_delete_task(land, founder):
    task = Task.objects.create(
        land=land,
        title="To delete",
        assigned_to=founder,
        created_by=founder,
        updated_by=founder,
    )
    res = _auth(founder).delete(f"{TASK_ENDPOINT}{task.pk}/")
    assert res.status_code in (200, 204)
    task.refresh_from_db()
    assert task.is_deleted is True
    # Default manager excludes soft-deleted
    assert Task.objects.filter(pk=task.pk).count() == 0
    assert Task.all_objects.filter(pk=task.pk).count() == 1


@pytest.mark.django_db
def test_list_excludes_deleted(land, founder):
    t1 = Task.objects.create(
        land=land,
        title="Keep",
        assigned_to=founder,
        created_by=founder,
        updated_by=founder,
    )
    t2 = Task.objects.create(
        land=land,
        title="Delete me",
        assigned_to=founder,
        created_by=founder,
        updated_by=founder,
    )
    t2.soft_delete(user=founder)

    res = _auth(founder).get(TASK_ENDPOINT)
    body = json.loads(res.content)
    ids = [item["id"] for item in body["data"]]
    assert str(t1.pk) in ids
    assert str(t2.pk) not in ids


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_unauthenticated_denied():
    res = APIClient().get(TASK_ENDPOINT)
    assert res.status_code == 401
