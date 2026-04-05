from rest_framework import serializers

from apps.documents.models import (
    DocumentKind,
    DocumentVersion,
    IdentityDocument,
    IdentityDocumentType,
    LandDocumentChecklistItem,
)


def mask_aadhaar(number: str) -> str:
    """Mask Aadhaar: 1234-5678-9012 → XXXX-XXXX-9012."""
    if not number:
        return ""
    cleaned = number.replace("-", "").replace(" ", "")
    if len(cleaned) < 12:
        return "X" * len(cleaned)
    return f"XXXX-XXXX-{cleaned[-4:]}"


def mask_pan(number: str) -> str:
    """Mask PAN: ABCDE1234F → XXXXX1234X."""
    if not number:
        return ""
    if len(number) < 10:
        return "X" * len(number)
    masked = "X" * 5 + number[5:9] + "X"
    return masked


def mask_document_number(doc_type: str, number: str) -> str:
    """Apply appropriate masking based on document type."""
    if doc_type == IdentityDocumentType.AADHAAR:
        return mask_aadhaar(number)
    elif doc_type == IdentityDocumentType.PAN:
        return mask_pan(number)
    return "X" * len(number) if number else ""


class LandDocumentChecklistItemSerializer(serializers.ModelSerializer):
    land_id = serializers.CharField(source="land.land_id", read_only=True)
    document_kind_display = serializers.CharField(
        source="get_document_kind_display", read_only=True
    )
    checklist_status_display = serializers.CharField(
        source="get_checklist_status_display", read_only=True
    )
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    updated_by_email = serializers.CharField(source="updated_by.email", read_only=True)

    class Meta:
        model = LandDocumentChecklistItem
        fields = (
            "id",
            "land",
            "land_id",
            "document_kind",
            "document_kind_display",
            "checklist_status",
            "checklist_status_display",
            "remarks",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_email",
            "updated_by",
            "updated_by_email",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


class LandDocumentChecklistItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandDocumentChecklistItem
        fields = ("land", "document_kind", "checklist_status", "remarks")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


class DocumentVersionSerializer(serializers.ModelSerializer):
    checklist_item_kind = serializers.CharField(
        source="checklist_item.document_kind", read_only=True
    )
    uploaded_by_email = serializers.CharField(
        source="uploaded_by.email", read_only=True
    )
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    updated_by_email = serializers.CharField(source="updated_by.email", read_only=True)

    class Meta:
        model = DocumentVersion
        fields = (
            "id",
            "checklist_item",
            "checklist_item_kind",
            "version_number",
            "s3_key",
            "original_filename",
            "content_type",
            "size_bytes",
            "uploaded_by",
            "uploaded_by_email",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_email",
            "updated_by",
            "updated_by_email",
        )
        read_only_fields = (
            "id",
            "version_number",
            "created_at",
            "updated_at",
            "uploaded_by",
            "created_by",
            "updated_by",
        )


class PresignedUploadRequestSerializer(serializers.Serializer):
    land_id = serializers.CharField()
    document_kind = serializers.ChoiceField(choices=DocumentKind.choices)
    filename = serializers.CharField(max_length=512)
    content_type = serializers.CharField(max_length=128)


class PresignedUploadResponseSerializer(serializers.Serializer):
    upload_url = serializers.URLField()
    s3_key = serializers.CharField(max_length=1024)
    expiry_seconds = serializers.IntegerField()


class ConfirmUploadRequestSerializer(serializers.Serializer):
    s3_key = serializers.CharField(max_length=1024)
    checklist_item_id = serializers.IntegerField()


class ConfirmUploadResponseSerializer(serializers.Serializer):
    version = DocumentVersionSerializer()


class PresignedDownloadRequestSerializer(serializers.Serializer):
    version_id = serializers.IntegerField()


class PresignedDownloadResponseSerializer(serializers.Serializer):
    download_url = serializers.URLField()
    expiry_seconds = serializers.IntegerField()


class IdentityDocumentSerializer(serializers.ModelSerializer):
    land_id = serializers.CharField(source="land.land_id", read_only=True)
    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    masked_document_number = serializers.SerializerMethodField()
    uploaded_by_email = serializers.CharField(
        source="uploaded_by.email", read_only=True
    )
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    updated_by_email = serializers.CharField(source="updated_by.email", read_only=True)

    class Meta:
        model = IdentityDocument
        fields = (
            "id",
            "land",
            "land_id",
            "document_type",
            "document_type_display",
            "document_number",
            "masked_document_number",
            "s3_key",
            "original_filename",
            "content_type",
            "uploaded_by",
            "uploaded_by_email",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_email",
            "updated_by",
            "updated_by_email",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "uploaded_by",
            "created_by",
            "updated_by",
        )

    def get_masked_document_number(self, obj) -> str:
        return mask_document_number(obj.document_type, obj.document_number)


class IdentityDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityDocument
        fields = (
            "land",
            "document_type",
            "document_number",
            "s3_key",
            "original_filename",
            "content_type",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "uploaded_by",
            "created_by",
            "updated_by",
        )
