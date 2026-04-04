import pytest

from apps.documents.models import (
    ChecklistStatus,
    DocumentKind,
    DocumentVersion,
    LandDocumentChecklistItem,
)
from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile


@pytest.fixture
def village(db):
    d = District.objects.create(name="Test District")
    t = Taluk.objects.create(name="Test Taluk", district=d)
    h = Hobli.objects.create(name="Test Hobli", taluk=t)
    return Village.objects.create(name="Test Village", hobli=h)


@pytest.mark.django_db
def test_checklist_and_version(village):
    land = LandFile.objects.create(village=village, survey_number="7")
    item = LandDocumentChecklistItem.objects.create(
        land=land,
        document_kind=DocumentKind.RTC,
        checklist_status=ChecklistStatus.CERTIFIED_OBTAINED,
    )
    ver = DocumentVersion.objects.create(
        checklist_item=item,
        version_number=1,
        s3_key="land/test/rtc_v1.pdf",
        original_filename="rtc.pdf",
    )
    assert item.versions.count() == 1
    assert ver.checklist_item_id == item.pk
