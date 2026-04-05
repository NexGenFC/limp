from datetime import date, timedelta

import pytest

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile
from apps.tasks.models import (
    NotificationLog,
    NotificationStatus,
    Task,
    TaskStatus,
)
from apps.tasks.tasks import check_overdue_tasks, send_task_assignment_notification
from apps.users.models import User, UserRole


@pytest.fixture
def village(db):
    d = District.objects.create(name="Test District")
    t = Taluk.objects.create(name="Test Taluk", district=d)
    h = Hobli.objects.create(name="Test Hobli", taluk=t)
    return Village.objects.create(name="Test Village", hobli=h)


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="worker@test.com",
        password="pw12345678",
        role=UserRole.FIELD_STAFF,
        phone="+919800000000",
    )


@pytest.fixture
def land(village, user):
    return LandFile.objects.create(
        village=village,
        survey_number="1",
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def task(land, user):
    return Task.objects.create(
        land=land,
        title="Test task",
        assigned_to=user,
        due_date=date.today() + timedelta(days=7),
        status=TaskStatus.OPEN,
    )


# ---------------------------------------------------------------------------
# send_task_assignment_notification
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_notification_creates_stub_log(task, settings):
    """Without WHATSAPP_API_TOKEN, a STUB log is created."""
    settings.WHATSAPP_API_TOKEN = ""

    send_task_assignment_notification.apply(args=[str(task.id)])

    logs = NotificationLog.objects.filter(task=task)
    assert logs.count() == 1
    assert logs.first().status == NotificationStatus.STUB


@pytest.mark.django_db
def test_notification_idempotent(task, settings):
    """Calling twice does not create a duplicate SENT log."""
    settings.WHATSAPP_API_TOKEN = ""

    send_task_assignment_notification.apply(args=[str(task.id)])
    send_task_assignment_notification.apply(args=[str(task.id)])

    # Both calls create STUB (not SENT), so re-invocations are allowed for
    # stub mode. The idempotency guard checks for SENT specifically.
    logs = NotificationLog.objects.filter(task=task)
    assert logs.count() == 2  # two STUBs — acceptable; guard is for SENT


@pytest.mark.django_db
def test_notification_skips_when_already_sent(task):
    """If a SENT log exists, no new log is created."""
    NotificationLog.objects.create(
        task=task,
        channel="WHATSAPP",
        status=NotificationStatus.SENT,
        message_summary="already sent",
    )

    send_task_assignment_notification.apply(args=[str(task.id)])

    assert NotificationLog.objects.filter(task=task).count() == 1


@pytest.mark.django_db
def test_notification_noop_for_missing_task(settings):
    """Non-existent task ID returns early without error."""
    settings.WHATSAPP_API_TOKEN = ""
    # Should not raise
    send_task_assignment_notification.apply(
        args=["00000000-0000-0000-0000-000000000000"]
    )
    assert NotificationLog.objects.count() == 0


# ---------------------------------------------------------------------------
# check_overdue_tasks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_overdue_scan_flips_status(land, user, settings):
    """Tasks past due_date get status=OVERDUE."""
    settings.WHATSAPP_API_TOKEN = ""
    past_task = Task.objects.create(
        land=land,
        title="Past due",
        assigned_to=user,
        due_date=date.today() - timedelta(days=1),
        status=TaskStatus.OPEN,
    )

    check_overdue_tasks.apply()

    past_task.refresh_from_db()
    assert past_task.status == TaskStatus.OVERDUE


@pytest.mark.django_db
def test_overdue_scan_skips_done_tasks(land, user, settings):
    """Already DONE tasks are not flipped to OVERDUE."""
    settings.WHATSAPP_API_TOKEN = ""
    done_task = Task.objects.create(
        land=land,
        title="Finished",
        assigned_to=user,
        due_date=date.today() - timedelta(days=1),
        status=TaskStatus.DONE,
    )

    check_overdue_tasks.apply()

    done_task.refresh_from_db()
    assert done_task.status == TaskStatus.DONE


@pytest.mark.django_db
def test_overdue_scan_enqueues_notifications(land, user, settings):
    """Overdue scan creates notification logs for flipped tasks."""
    settings.WHATSAPP_API_TOKEN = ""
    Task.objects.create(
        land=land,
        title="Overdue task",
        assigned_to=user,
        due_date=date.today() - timedelta(days=2),
        status=TaskStatus.IN_PROGRESS,
    )

    check_overdue_tasks.apply()

    # The chained send_task_assignment_notification should have created a log
    assert NotificationLog.objects.count() >= 1
