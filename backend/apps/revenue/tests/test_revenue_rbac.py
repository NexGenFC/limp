import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.revenue.models import GovernmentWorkflow
from apps.geography.models import Village, Hobli, Taluk, District
from apps.land.models import LandFile
from apps.users.models import UserRole

User = get_user_model()


@pytest.mark.django_db
class TestRevenueRBAC:
    def test_advocate_access_denied_403(self):
        """Requirement §3.3 & §3.4: Prove ADVOCATE receives 403 Forbidden."""
        client = APIClient()
        advocate = User.objects.create_user(
            username="test_advocate",
            email="advocate@example.com",  # Email added
            password="password123",
            role=UserRole.EXTERNAL_ADVOCATE,
        )
        client.force_authenticate(user=advocate)
        url = reverse("government-workflow-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_field_staff_access_denied_403(self):
        """Requirement §3.3 & §3.4: Prove FIELD_STAFF receives 403 Forbidden."""
        client = APIClient()
        field_staff = User.objects.create_user(
            username="test_field_staff",
            email="field@example.com",
            password="password123",
            role=UserRole.FIELD_STAFF,
        )
        client.force_authenticate(user=field_staff)
        url = reverse("government-workflow-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_revenue_team_full_crud_success(self):
        """Requirement §3.3: Verify REVENUE_TEAM can create and list."""
        client = APIClient()
        revenue_user = User.objects.create_user(
            username="rev_user",
            email="rev@example.com",  # Fixed: Email added
            role=UserRole.REVENUE_TEAM,
            password="password123",
        )
        client.force_authenticate(user=revenue_user)

        dist = District.objects.create(name="D1")
        taluk = Taluk.objects.create(name="T1", district=dist)
        hobli = Hobli.objects.create(name="H1", taluk=taluk)
        village = Village.objects.create(name="V1", hobli=hobli)
        land = LandFile.objects.create(land_id="LAND-002", village=village)

        url = reverse("government-workflow-list")
        data = {"land": str(land.id), "kind": "PHODI", "status": "APPLIED"}

        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["created_by"] is not None
        workflow_id = response.data["id"]

        # Test List (GET)
        response_list = client.get(url)
        assert response_list.status_code == status.HTTP_200_OK
        assert len(response_list.data) == 1

        # Test Update (PATCH)
        detail_url = reverse("government-workflow-detail", args=[workflow_id])
        update_data = {"status": "IN_PROGRESS"}
        response_update = client.patch(detail_url, update_data)
        assert response_update.status_code == status.HTTP_200_OK
        assert response_update.data["status"] == "IN_PROGRESS"

    def test_soft_delete_integrity(self):
        """Requirement §3.3: Verify delete hides record instead of erasing it."""
        client = APIClient()
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",  # Fixed: Email added
            role=UserRole.MANAGEMENT,
        )
        client.force_authenticate(user=admin)

        dist = District.objects.create(name="D2")
        taluk = Taluk.objects.create(name="T2", district=dist)
        hobli = Hobli.objects.create(name="H2", taluk=taluk)
        village = Village.objects.create(name="V2", hobli=hobli)
        land = LandFile.objects.create(land_id="LAND-003", village=village)
        workflow = GovernmentWorkflow.objects.create(land=land, kind="MUTATION")

        url = reverse("government-workflow-detail", args=[workflow.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        workflow.refresh_from_db()
        assert workflow.is_deleted is True
