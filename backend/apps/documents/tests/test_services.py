import pytest
from unittest.mock import MagicMock, patch

from apps.documents.services import (
    S3NotConfiguredError,
    _is_configured,
    generate_presigned_download_url,
    generate_presigned_upload_url,
    check_object_exists,
    get_overall_completion_stats,
)


class TestS3Service:
    def test_is_configured_when_bucket_not_set(self, settings):
        settings.AWS_S3_BUCKET_NAME = None
        assert _is_configured() is False

    def test_is_configured_when_bucket_set(self, settings):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        assert _is_configured() is True

    def test_generate_presigned_upload_url_not_configured(self, settings):
        settings.AWS_S3_BUCKET_NAME = None
        with pytest.raises(S3NotConfiguredError):
            generate_presigned_upload_url("key", "text/plain", "file.txt")

    @patch("apps.documents.services._get_s3_client")
    def test_generate_presigned_upload_url_success(self, mock_get_client, settings):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        settings.AWS_S3_REGION_NAME = "us-east-1"
        settings.AWS_S3_PRESIGN_EXPIRY_SECONDS = 3600

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = (
            "https://s3.example.com/upload"
        )
        mock_get_client.return_value = mock_client

        url, expiry = generate_presigned_upload_url(
            "test/key/file.pdf", "application/pdf", "file.pdf"
        )

        assert url == "https://s3.example.com/upload"
        assert expiry == 3600
        mock_client.generate_presigned_url.assert_called_once()

    def test_generate_presigned_download_url_not_configured(self, settings):
        settings.AWS_S3_BUCKET_NAME = None
        with pytest.raises(S3NotConfiguredError):
            generate_presigned_download_url("test/key")

    @patch("apps.documents.services._get_s3_client")
    def test_generate_presigned_download_url_success(self, mock_get_client, settings):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        settings.AWS_S3_REGION_NAME = "us-east-1"
        settings.AWS_S3_PRESIGN_EXPIRY_SECONDS = 3600

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = (
            "https://s3.example.com/download"
        )
        mock_get_client.return_value = mock_client

        url, expiry = generate_presigned_download_url("test/key/file.pdf")

        assert url == "https://s3.example.com/download"
        assert expiry == 3600

    def test_check_object_exists_not_configured(self, settings):
        settings.AWS_S3_BUCKET_NAME = None
        with pytest.raises(S3NotConfiguredError):
            check_object_exists("test/key")

    @patch("apps.documents.services._get_s3_client")
    def test_check_object_exists_success(self, mock_get_client, settings):
        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        settings.AWS_S3_REGION_NAME = "us-east-1"

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = check_object_exists("test/key/file.pdf")

        mock_client.head_object.assert_called_once_with(
            Bucket="test-bucket", Key="test/key/file.pdf"
        )
        assert result is True

    @patch("apps.documents.services._get_s3_client")
    def test_check_object_exists_not_found(self, mock_get_client, settings):
        from botocore.exceptions import ClientError

        settings.AWS_S3_BUCKET_NAME = "test-bucket"
        settings.AWS_S3_REGION_NAME = "us-east-1"

        mock_client = MagicMock()
        mock_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
        )
        mock_get_client.return_value = mock_client

        result = check_object_exists("test/key/nonexistent.pdf")

        assert result is False


class TestCompletionStatsService:
    @patch("apps.land.models.LandFile.objects")
    def test_calculate_land_completion_land_not_found(self, mock_land_objects):
        from apps.documents.services import calculate_land_completion
        from apps.land.models import LandFile

        mock_land_objects.get.side_effect = LandFile.DoesNotExist

        with pytest.raises(ValueError, match="Land with land_id"):
            calculate_land_completion("NONEXISTENT-001")

    @patch("apps.land.models.LandFile.objects")
    def test_calculate_land_completion_no_items(self, mock_land_objects, settings):
        from apps.documents.services import calculate_land_completion

        settings.AWS_S3_BUCKET_NAME = None

        land = MagicMock()
        land.land_id = "LIMP-2024-0001"
        mock_land_objects.get.return_value = land

        mock_items = MagicMock()
        mock_items.exclude.return_value.count.return_value = 0

        with patch(
            "apps.documents.services.LandDocumentChecklistItem.objects.filter",
            return_value=mock_items,
        ):
            result = calculate_land_completion("LIMP-2024-0001")
            assert result == 0.0

    @patch("apps.land.models.LandFile.objects")
    def test_get_overall_completion_stats_no_lands(self, mock_land_objects):
        mock_land_objects.filter.return_value.exists.return_value = False

        result = get_overall_completion_stats()
        assert result == 0.0
