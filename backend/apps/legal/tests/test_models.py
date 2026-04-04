import pytest

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile
from apps.legal.models import LegalCase


@pytest.fixture
def village(db):
    d = District.objects.create(name="Test District")
    t = Taluk.objects.create(name="Test Taluk", district=d)
    h = Hobli.objects.create(name="Test Hobli", taluk=t)
    return Village.objects.create(name="Test Village", hobli=h)


@pytest.mark.django_db
def test_legal_case_land_fk(village):
    land = LandFile.objects.create(village=village, survey_number="42")
    case = LegalCase.objects.create(land=land, case_number="OS 1/2026")
    assert case.land_id == land.pk
    assert land.legal_cases.count() == 1
