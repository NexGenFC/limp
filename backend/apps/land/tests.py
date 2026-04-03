import json

import pytest
from rest_framework.test import APIClient

from apps.geography.models import District, Hobli, Taluk, Village
from apps.land.models import LandFile
from apps.users.models import User, UserRole

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def village(db):
    d = District.objects.create(name="Bengaluru Rural")
    t = Taluk.objects.create(name="Devanahalli", district=d)
    h = Hobli.objects.create(name="Devanahalli", taluk=t)
    return Village.objects.create(name="Budigere", hobli=h)


def _make_user(db, role, suffix=""):
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
    return _make_user(db, UserRole.FOUNDER)


@pytest.fixture
def management(db):
    return _make_user(db, UserRole.MANAGEMENT)


@pytest.fixture
def inhouse_advocate(db):
    return _make_user(db, UserRole.IN_HOUSE_ADVOCATE)


@pytest.fixture
def external_advocate(db):
    return _make_user(db, UserRole.EXTERNAL_ADVOCATE)


@pytest.fixture
def revenue_team(db):
    return _make_user(db, UserRole.REVENUE_TEAM)


@pytest.fixture
def surveyor_inhouse(db):
    return _make_user(db, UserRole.SURVEYOR_INHOUSE)


@pytest.fixture
def surveyor_freelance(db):
    return _make_user(db, UserRole.SURVEYOR_FREELANCE)


@pytest.fixture
def field_staff(db):
    return _make_user(db, UserRole.FIELD_STAFF)


LAND_PAYLOAD = {
    "survey_number": "101",
    "hissa": "A",
    "extent_acres": "5.0000",
    "classification": "AGRICULTURAL",
}


# ---------------------------------------------------------------------------
# CRUD basics (FOUNDER has full access)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_create_land_file(founder, village):
    res = _auth(founder).post(
        "/api/v1/land/",
        {**LAND_PAYLOAD, "village": village.pk},
        format="json",
    )
    assert res.status_code == 201
    body = json.loads(res.content)
    assert body["success"] is True
    assert body["data"]["land_id"].startswith("LIMP-")
    assert body["data"]["village_name"] == "Budigere"
    assert body["data"]["district_name"] == "Bengaluru Rural"


@pytest.mark.django_db
def test_soft_delete_land_file(founder, village):
    lf = LandFile.objects.create(
        village=village, survey_number="202", created_by=founder, updated_by=founder
    )
    res = _auth(founder).delete(f"/api/v1/land/{lf.pk}/")
    assert res.status_code in (200, 204)
    lf.refresh_from_db()
    assert lf.is_deleted is True
    assert LandFile.objects.filter(pk=lf.pk).count() == 0
    assert LandFile.all_objects.filter(pk=lf.pk).count() == 1


@pytest.mark.django_db
def test_list_excludes_deleted(founder, village):
    lf1 = LandFile.objects.create(
        village=village, survey_number="301", created_by=founder, updated_by=founder
    )
    lf2 = LandFile.objects.create(
        village=village, survey_number="302", created_by=founder, updated_by=founder
    )
    lf1.soft_delete(user=founder)
    res = _auth(founder).get("/api/v1/land/")
    body = json.loads(res.content)
    ids = [item["id"] for item in body["data"]]
    assert lf2.pk in ids
    assert lf1.pk not in ids


# ---------------------------------------------------------------------------
# RBAC — role matrix (PRD §3.2)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_management_full_crud(management, village):
    client = _auth(management)
    res = client.post(
        "/api/v1/land/",
        {**LAND_PAYLOAD, "village": village.pk},
        format="json",
    )
    assert res.status_code == 201
    pk = json.loads(res.content)["data"]["id"]

    res = client.patch(
        f"/api/v1/land/{pk}/",
        {"survey_number": "102"},
        format="json",
    )
    assert res.status_code == 200

    res = client.delete(f"/api/v1/land/{pk}/")
    assert res.status_code in (200, 204)


@pytest.mark.django_db
class TestReadOnlyRoles:
    """IN_HOUSE_ADVOCATE, REVENUE_TEAM, SURVEYOR_INHOUSE may read but not write."""

    @pytest.fixture(autouse=True)
    def _seed(self, founder, village):
        self.land = LandFile.objects.create(
            village=village,
            survey_number="500",
            created_by=founder,
            updated_by=founder,
        )

    @pytest.mark.parametrize(
        "role_fixture",
        ["inhouse_advocate", "revenue_team", "surveyor_inhouse"],
    )
    def test_list_allowed(self, role_fixture, request):
        user = request.getfixturevalue(role_fixture)
        res = _auth(user).get("/api/v1/land/")
        assert res.status_code == 200

    @pytest.mark.parametrize(
        "role_fixture",
        ["inhouse_advocate", "revenue_team", "surveyor_inhouse"],
    )
    def test_detail_allowed(self, role_fixture, request):
        user = request.getfixturevalue(role_fixture)
        res = _auth(user).get(f"/api/v1/land/{self.land.pk}/")
        assert res.status_code == 200

    @pytest.mark.parametrize(
        "role_fixture",
        ["inhouse_advocate", "revenue_team", "surveyor_inhouse"],
    )
    def test_create_denied(self, role_fixture, village, request):
        user = request.getfixturevalue(role_fixture)
        res = _auth(user).post(
            "/api/v1/land/",
            {**LAND_PAYLOAD, "village": village.pk},
            format="json",
        )
        assert res.status_code == 403

    @pytest.mark.parametrize(
        "role_fixture",
        ["inhouse_advocate", "revenue_team", "surveyor_inhouse"],
    )
    def test_delete_denied(self, role_fixture, request):
        user = request.getfixturevalue(role_fixture)
        res = _auth(user).delete(f"/api/v1/land/{self.land.pk}/")
        assert res.status_code == 403


@pytest.mark.django_db
class TestDeniedRoles:
    """EXTERNAL_ADVOCATE, SURVEYOR_FREELANCE, FIELD_STAFF: no land access."""

    @pytest.fixture(autouse=True)
    def _seed(self, founder, village):
        self.land = LandFile.objects.create(
            village=village,
            survey_number="600",
            created_by=founder,
            updated_by=founder,
        )

    @pytest.mark.parametrize(
        "role_fixture",
        ["external_advocate", "surveyor_freelance", "field_staff"],
    )
    def test_list_denied(self, role_fixture, request):
        user = request.getfixturevalue(role_fixture)
        res = _auth(user).get("/api/v1/land/")
        assert res.status_code == 403

    @pytest.mark.parametrize(
        "role_fixture",
        ["external_advocate", "surveyor_freelance", "field_staff"],
    )
    def test_create_denied(self, role_fixture, village, request):
        user = request.getfixturevalue(role_fixture)
        res = _auth(user).post(
            "/api/v1/land/",
            {**LAND_PAYLOAD, "village": village.pk},
            format="json",
        )
        assert res.status_code == 403


@pytest.mark.django_db
def test_unauthenticated_denied():
    res = APIClient().get("/api/v1/land/")
    assert res.status_code == 401
