"""Celery tasks for legal / POA compliance (beat schedules in settings)."""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.legal.models import Hearing, PlanOfAction, POAStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_poa_overdue(self):
    today = timezone.localdate()
    qs = PlanOfAction.objects.filter(
        status=POAStatus.PENDING,
        deadline__lt=today,
    )
    for poa in qs.iterator():
        poa.status = POAStatus.OVERDUE
        poa.save(update_fields=["status"])
        logger.info(
            "POA marked overdue",
            extra={"poa_id": str(poa.pk)},
        )
        # TODO: enqueue notification (Person 3)


@shared_task(bind=True, max_retries=3)
def create_poa_compliance_tasks(self):
    target_date = timezone.localdate() + timedelta(days=5)
    hearings = (
        Hearing.objects.filter(
            hearing_date=target_date,
            poa__isnull=True,
        )
        .select_related("case", "case__land")
        .iterator()
    )
    for hearing in hearings:
        PlanOfAction.objects.create(
            hearing=hearing,
            land=hearing.case.land,
            status=POAStatus.PENDING,
            deadline=PlanOfAction.compute_deadline(hearing.hearing_date),
        )
        logger.info(
            "POA compliance row created",
            extra={"hearing_id": str(hearing.pk)},
        )
        # TODO: enqueue notification (Person 3)
