from rest_framework import serializers

from apps.documents.models import (
    DocumentKind,
    DocumentVersion,
    LandDocumentChecklistItem,
)


class LandDocumentChecklistItemSerializer(serializers.ModelSerializer):
    land_id = serializers.CharField(source="land.land_id", read_only=True)
    document_kind_display = serializers.CharField(
        source="get_document_kind_display", read_only=True
    )
    checklist_status_display = serializers.CharField(
        source="get_checklist_status_display", read_only=True
    )

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
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LandDocumentChecklistItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandDocumentChecklistItem
        fields = ("land", "document_kind", "checklist_status", "remarks")


class DocumentVersionSerializer(serializers.ModelSerializer):
    checklist_item_kind = serializers.CharField(
        source="checklist_item.document_kind", read_only=True
    )
    uploaded_by_email = serializers.CharField(
        source="uploaded_by.email", read_only=True
    )

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
        )
        read_only_fields = (
            "id",
            "version_number",
            "created_at",
            "uploaded_by",
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
