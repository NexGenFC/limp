from unittest.mock import MagicMock

from apps.documents.serializers import (
    mask_aadhaar,
    mask_pan,
    mask_document_number,
    IdentityDocumentSerializer,
    IdentityDocumentCreateSerializer,
)
from apps.documents.models import IdentityDocumentType


class TestMaskingFunctions:
    def test_mask_aadhaar_full_number(self):
        assert mask_aadhaar("1234-5678-9012") == "XXXX-XXXX-9012"

    def test_mask_aadhaar_without_dashes(self):
        assert mask_aadhaar("123456789012") == "XXXX-XXXX-9012"

    def test_mask_aadhaar_short_number(self):
        assert mask_aadhaar("123456") == "XXXXXX"

    def test_mask_aadhaar_empty(self):
        assert mask_aadhaar("") == ""

    def test_mask_pan_full_number(self):
        assert mask_pan("ABCDE1234F") == "XXXXX1234X"

    def test_mask_pan_short_number(self):
        assert mask_pan("ABC12") == "XXXXX"

    def test_mask_pan_empty(self):
        assert mask_pan("") == ""

    def test_mask_document_number_aadhaar(self):
        result = mask_document_number(IdentityDocumentType.AADHAAR, "1234-5678-9012")
        assert result == "XXXX-XXXX-9012"

    def test_mask_document_number_pan(self):
        result = mask_document_number(IdentityDocumentType.PAN, "ABCDE1234F")
        assert result == "XXXXX1234X"

    def test_mask_document_number_other(self):
        result = mask_document_number(IdentityDocumentType.PASSPORT, "ABC123")
        assert result == "XXXXXX"


class TestIdentityDocumentSerializer:
    def test_serializer_masked_document_number_aadhaar(self):
        mock_obj = MagicMock()
        mock_obj.document_type = IdentityDocumentType.AADHAAR
        mock_obj.document_number = "1234-5678-9012"

        serializer = IdentityDocumentSerializer()
        result = serializer.get_masked_document_number(mock_obj)

        assert result == "XXXX-XXXX-9012"

    def test_serializer_masked_document_number_pan(self):
        mock_obj = MagicMock()
        mock_obj.document_type = IdentityDocumentType.PAN
        mock_obj.document_number = "ABCDE1234F"

        serializer = IdentityDocumentSerializer()
        result = serializer.get_masked_document_number(mock_obj)

        assert result == "XXXXX1234X"

    def test_serializer_fields_include_masked(self):
        serializer = IdentityDocumentSerializer()
        fields = serializer.Meta.fields
        assert "masked_document_number" in fields

    def test_create_serializer_fields(self):
        serializer = IdentityDocumentCreateSerializer()
        fields = serializer.Meta.fields
        assert "land" in fields
        assert "document_type" in fields
        assert "document_number" in fields
        assert "s3_key" in fields
