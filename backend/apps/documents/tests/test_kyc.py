from unittest.mock import MagicMock, patch

from apps.documents.serializers import IdentityDocumentSerializer
from apps.documents.models import IdentityDocument, IdentityDocumentType
from apps.land.serializers import LandFileSerializer


class TestIdentityDocumentMasking:
    """Verify identity document numbers are masked in API responses."""

    def test_aadhaar_masked_in_api_response(self):
        doc = MagicMock(spec=IdentityDocument)
        doc.document_type = IdentityDocumentType.AADHAAR
        doc.document_number = "1234-5678-9012"

        serializer = IdentityDocumentSerializer()
        result = serializer.get_masked_document_number(doc)

        assert result == "XXXX-XXXX-9012"
        assert "1234" not in result
        assert "5678" not in result
        assert "9012" in result

    def test_pan_masked_in_api_response(self):
        doc = MagicMock(spec=IdentityDocument)
        doc.document_type = IdentityDocumentType.PAN
        doc.document_number = "ABCDE1234F"

        serializer = IdentityDocumentSerializer()
        result = serializer.get_masked_document_number(doc)

        assert result == "XXXXX1234X"
        assert "ABCDE" not in result
        assert "1234" in result

    def test_passport_other_masked(self):
        doc = MagicMock(spec=IdentityDocument)
        doc.document_type = IdentityDocumentType.PASSPORT
        doc.document_number = "AB1234"

        serializer = IdentityDocumentSerializer()
        result = serializer.get_masked_document_number(doc)

        assert result == "XXXXXX"


class TestLandFileCompletionPercentage:
    """Verify completion_percentage in LandFileSerializer matches formula."""

    @patch("apps.land.serializers.calculate_land_completion")
    def test_completion_percentage_formula_correct(self, mock_calculate):
        mock_calculate.return_value = 0.75

        mock_land = MagicMock()
        mock_land.land_id = "LIMP-2024-0001"
        mock_land.village = MagicMock()
        mock_land.village.name = "Test Village"
        mock_land.village.hobli = MagicMock()
        mock_land.village.hobli.name = "Test Hobli"
        mock_land.village.hobli.taluk = MagicMock()
        mock_land.village.hobli.taluk.name = "Test Taluk"
        mock_land.village.hobli.taluk.district = MagicMock()
        mock_land.village.hobli.taluk.district.name = "Test District"

        serializer = LandFileSerializer()
        result = serializer.get_completion_percentage(mock_land)

        assert result == 0.75
        mock_calculate.assert_called_once_with("LIMP-2024-0001")

    @patch("apps.land.serializers.calculate_land_completion")
    def test_completion_percentage_returns_zero_on_error(self, mock_calculate):
        mock_calculate.side_effect = ValueError("Land not found")

        mock_land = MagicMock()
        mock_land.land_id = "INVALID-001"
        mock_land.village = MagicMock()
        mock_land.village.hobli = MagicMock()
        mock_land.village.hobli.taluk = MagicMock()

        serializer = LandFileSerializer()
        result = serializer.get_completion_percentage(mock_land)

        assert result == 0.0
