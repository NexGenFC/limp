import pytest

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile
from apps.tasks.models import (
    NotificationChannel,
    NotificationLog,
    NotificationStatus,
    Task,
    TaskStatus,
)
from apps.users.models import User, UserRole


@pytest.fixture
def village(db):
    d = District.objects.create(name="Test District")
    t = Taluk.objects.create(name="Test Taluk", district=d)
    h = Hobli.objects.create(name="Test Hobli", taluk=t)
    return Village.objects.create(name="Test Village", hobli=h)


@pytest.mark.django_db
def test_task_and_notification_log(village):
    land = LandFile.objects.create(village=village, survey_number="1")
    user = User.objects.create_user(
        email="assignee@test.com",
        password="pw12345678",
        role=UserRole.FIELD_STAFF,
    )
    task = Task.objects.create(
        land=land,
        title="Follow up with VA",
        assigned_to=user,
        status=TaskStatus.OPEN,
    )
    log = NotificationLog.objects.create(
        task=task,
        channel=NotificationChannel.INTERNAL,
        status=NotificationStatus.STUB,
        message_summary="queued",
    )
    assert task.notification_logs.count() == 1
    assert log.task_id == task.pk
