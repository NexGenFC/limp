import pytest
from django.db import IntegrityError

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile
from apps.revenue.models import GovernmentWorkflow, WorkflowKind, WorkflowStatus


@pytest.fixture
def village(db):
    d = District.objects.create(name="Test District")
    t = Taluk.objects.create(name="Test Taluk", district=d)
    h = Hobli.objects.create(name="Test Hobli", taluk=t)
    return Village.objects.create(name="Test Village", hobli=h)


@pytest.mark.django_db
def test_government_workflow_unique_per_land_kind(village):
    land = LandFile.objects.create(village=village, survey_number="9")
    GovernmentWorkflow.objects.create(
        land=land,
        kind=WorkflowKind.MUTATION,
        status=WorkflowStatus.APPLIED,
    )
    with pytest.raises(IntegrityError):
        GovernmentWorkflow.objects.create(
            land=land,
            kind=WorkflowKind.MUTATION,
            status=WorkflowStatus.NOT_STARTED,
        )
