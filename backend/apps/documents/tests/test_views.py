import pytest
from unittest.mock import MagicMock, patch
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.documents.views import (
    PresignedUploadView,
    PresignedDownloadView,
    ConfirmUploadView,
)
from apps.users.models import UserRole


@pytest.fixture
def request_factory():
    return APIRequestFactory()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.is_authenticated = True
    user.role = UserRole.MANAGEMENT
    user.id = 1
    user.pk = 1
    return user


@pytest.fixture
def mock_user_in_house_advocate():
    user = MagicMock()
    user.is_authenticated = True
    user.role = UserRole.IN_HOUSE_ADVOCATE
    user.id = 2
    user.pk = 2
    return user


@pytest.fixture
def mock_user_field_staff():
    user = MagicMock()
    user.is_authenticated = True
    user.role = UserRole.FIELD_STAFF
    user.id = 3
    user.pk = 3
    return user


@pytest.mark.django_db
class TestPresignedUploadView:
    @patch("apps.documents.views.LandDocumentChecklistItem.objects")
    @patch("apps.documents.views.generate_presigned_upload_url")
    def test_presigned_upload_not_configured(
        self, mock_generate, mock_objects, request_factory, settings, mock_user
    ):
        settings.AWS_S3_BUCKET_NAME = None
        mock_objects.get.side_effect = Exception("DB should not be hit")

        request = request_factory.post(
            "/api/v1/documents/presigned-upload",
            data={
                "land_id": "LIMP-2024-0001",
                "document_kind": "RTC",
                "filename": "test.pdf",
                "content_type": "application/pdf",
            },
        )
        force_authenticate(request, user=mock_user)

        view = PresignedUploadView.as_view()
        response = view(request)

        assert response.status_code == 503
        assert "S3 not configured" in str(response.data["error"])

    @patch("apps.documents.views.LandDocumentChecklistItem.objects")
    @patch("apps.documents.views.generate_presigned_upload_url")
    def test_presigned_upload_rbac_forbidden_role(
        self,
        mock_generate,
        mock_objects,
        request_factory,
        settings,
        mock_user_field_staff,
    ):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"

        request = request_factory.post(
            "/api/v1/documents/presigned-upload",
            data={
                "land_id": "LIMP-2024-0001",
                "document_kind": "RTC",
                "filename": "test.pdf",
                "content_type": "application/pdf",
            },
        )
        force_authenticate(request, user=mock_user_field_staff)

        view = PresignedUploadView.as_view()
        response = view(request)

        assert response.status_code == 403

    @patch("apps.documents.views.LandDocumentChecklistItem.objects")
    @patch("apps.documents.views.generate_presigned_upload_url")
    def test_presigned_upload_rbac_readonly_role_cannot_write(
        self,
        mock_generate,
        mock_objects,
        request_factory,
        settings,
        mock_user_in_house_advocate,
    ):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        mock_generate.return_value = ("https://s3.example.com/upload", 3600)

        request = request_factory.post(
            "/api/v1/documents/presigned-upload",
            data={
                "land_id": "LIMP-2024-0001",
                "document_kind": "RTC",
                "filename": "test.pdf",
                "content_type": "application/pdf",
            },
        )
        force_authenticate(request, user=mock_user_in_house_advocate)

        view = PresignedUploadView.as_view()
        response = view(request)

        assert response.status_code == 403


@pytest.mark.django_db
class TestPresignedDownloadView:
    @patch("apps.documents.views.DocumentVersion.objects")
    @patch("apps.documents.views.generate_presigned_download_url")
    def test_presigned_download_not_configured(
        self, mock_generate, mock_objects, request_factory, settings, mock_user
    ):
        settings.AWS_S3_BUCKET_NAME = None
        mock_objects.get.side_effect = Exception("DB should not be hit")

        request = request_factory.post(
            "/api/v1/documents/presigned-download",
            data={"version_id": 1},
        )
        force_authenticate(request, user=mock_user)

        view = PresignedDownloadView.as_view()
        response = view(request)

        assert response.status_code == 503
        assert "S3 not configured" in str(response.data["error"])

    @patch("apps.documents.views.DocumentVersion.objects")
    @patch("apps.documents.views.generate_presigned_download_url")
    def test_presigned_download_rbac_forbidden_role(
        self,
        mock_generate,
        mock_objects,
        request_factory,
        settings,
        mock_user_field_staff,
    ):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"

        request = request_factory.post(
            "/api/v1/documents/presigned-download",
            data={"version_id": 1},
        )
        force_authenticate(request, user=mock_user_field_staff)

        view = PresignedDownloadView.as_view()
        response = view(request)

        assert response.status_code == 403

    @patch("apps.documents.views.DocumentVersion.objects")
    @patch("apps.documents.views.generate_presigned_download_url")
    def test_presigned_download_rbac_readonly_allowed(
        self,
        mock_generate,
        mock_objects,
        request_factory,
        settings,
        mock_user_in_house_advocate,
    ):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        mock_generate.return_value = ("https://s3.example.com/download", 3600)

        mock_qs = MagicMock()
        mock_objects.select_related.return_value.filter.return_value.filter.return_value.distinct.return_value = mock_qs
        mock_qs.get.return_value = MagicMock(s3_key="test-key")

        request = request_factory.post(
            "/api/v1/documents/presigned-download",
            data={"version_id": 1},
        )
        force_authenticate(request, user=mock_user_in_house_advocate)

        view = PresignedDownloadView.as_view()
        response = view(request)

        assert response.status_code == 200
        assert response.data["download_url"] == "https://s3.example.com/download"


@pytest.mark.django_db
class TestConfirmUploadView:
    @patch("apps.documents.views._is_configured")
    def test_confirm_upload_not_configured(
        self, mock_is_configured, request_factory, settings, mock_user
    ):
        settings.AWS_S3_BUCKET_NAME = None
        mock_is_configured.return_value = False

        request = request_factory.post(
            "/api/v1/documents/confirm-upload",
            data={
                "s3_key": "documents/LIMP-2024-0001/RTC/test.pdf",
                "checklist_item_id": 1,
            },
        )
        force_authenticate(request, user=mock_user)

        view = ConfirmUploadView.as_view()
        response = view(request)

        assert response.status_code == 503

    def test_confirm_upload_rbac_forbidden_role(
        self, request_factory, settings, mock_user_field_staff
    ):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"

        request = request_factory.post(
            "/api/v1/documents/confirm-upload",
            data={
                "s3_key": "documents/LIMP-2024-0001/RTC/test.pdf",
                "checklist_item_id": 1,
            },
        )
        force_authenticate(request, user=mock_user_field_staff)

        view = ConfirmUploadView.as_view()
        response = view(request)

        assert response.status_code == 403
