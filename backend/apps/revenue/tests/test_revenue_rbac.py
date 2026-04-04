import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.revenue.models import GovernmentWorkflow
from apps.geography.models import Village, Hobli, Taluk, District
from apps.land.models import LandFile
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
class TestRevenueRBAC:
    def test_advocate_access_denied_403(self):
        """Requirement §3.3 & §3.4: Prove ADVOCATE receives 403 Forbidden."""
        # 1. Use APIClient for DRF compatibility
        client = APIClient()

        # 2. Create the Advocate user
        advocate = User.objects.create_user(
            username="test_advocate",
            email="advocate@example.com",
            password="password123",
            role="EXTERNAL_ADVOCATE",
        )

        # 3. Use force_authenticate to bypass Token/Session issues
        client.force_authenticate(user=advocate)

        # 4. Attempt to list workflows
        url = reverse("government-workflow-list")
        response = client.get(url)

        # 5. NOW it should return 403 (Authenticated but No Permission)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_days_pending_logic(self):
        """Requirement §3.2 & §3.4: Verify the math for days_pending."""
        # Create Geography hierarchy
        dist = District.objects.create(name="Test Dist")
        taluk = Taluk.objects.create(name="Test Taluk", district=dist)
        hobli = Hobli.objects.create(name="Test Hobli", taluk=taluk)
        village = Village.objects.create(name="Test Village", hobli=hobli)

        # Setup land file
        land = LandFile.objects.create(land_id="TEST-001", village=village)

        # Set applied_on to 10 days ago
        ten_days_ago = timezone.now().date() - timedelta(days=10)
        workflow = GovernmentWorkflow.objects.create(
            land=land, kind="MUTATION", applied_on=ten_days_ago
        )

        assert workflow.days_pending == 10
