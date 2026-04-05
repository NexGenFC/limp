"""Document vault API views with presigned URL support."""

import uuid

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import DocumentVersion, LandDocumentChecklistItem
from apps.documents.serializers import (
    ConfirmUploadRequestSerializer,
    ConfirmUploadResponseSerializer,
    DocumentVersionSerializer,
    LandDocumentChecklistItemSerializer,
    PresignedDownloadRequestSerializer,
    PresignedDownloadResponseSerializer,
    PresignedUploadRequestSerializer,
    PresignedUploadResponseSerializer,
)
from apps.documents.services import (
    S3ServiceError,
    _is_configured,
    check_object_exists,
    generate_presigned_download_url,
    generate_presigned_upload_url,
)
from apps.users.permissions import DocumentPermission


class LandDocumentChecklistViewSet(viewsets.ModelViewSet):
    """CRUD for land document checklist items."""

    serializer_class = LandDocumentChecklistItemSerializer
    permission_classes = [DocumentPermission]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = LandDocumentChecklistItem.objects.select_related("land").filter(
            is_deleted=False
        )

        land_id = self.request.query_params.get("land_id")
        if land_id:
            queryset = queryset.filter(land__land_id=land_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class DocumentVersionViewSet(viewsets.ModelViewSet):
    """CRUD for document versions."""

    serializer_class = DocumentVersionSerializer
    permission_classes = [DocumentPermission]
    http_method_names = ["get", "delete", "head", "options"]

    def get_queryset(self):
        return (
            DocumentVersion.objects.filter(is_deleted=False)
            .select_related("checklist_item__land")
            .order_by("-version_number")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentVersionSerializer
        return DocumentVersionSerializer

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class PresignedUploadView(APIView):
    """Generate a presigned URL for uploading a document."""

    permission_classes = [DocumentPermission]

    def post(self, request):
        serializer = PresignedUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        land_id = serializer.validated_data["land_id"]
        document_kind = serializer.validated_data["document_kind"]
        filename = serializer.validated_data["filename"]
        content_type = serializer.validated_data["content_type"]

        if not _is_configured():
            return Response(
                {
                    "error": "S3 not configured",
                    "detail": "AWS_S3_BUCKET_NAME is not set",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            LandDocumentChecklistItem.objects.get(
                land__land_id=land_id,
                document_kind=document_kind,
                is_deleted=False,
            )
        except LandDocumentChecklistItem.DoesNotExist:
            return Response(
                {
                    "error": "Checklist item not found",
                    "detail": f"No checklist item for land {land_id} and document kind {document_kind}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        s3_key = f"documents/{land_id}/{document_kind}/{uuid.uuid4()}/{filename}"

        try:
            upload_url, expiry = generate_presigned_upload_url(
                s3_key=s3_key,
                content_type=content_type,
                filename=filename,
            )
        except S3ServiceError as e:
            return Response(
                {"error": "Failed to generate upload URL", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_serializer = PresignedUploadResponseSerializer(
            {"upload_url": upload_url, "s3_key": s3_key, "expiry_seconds": expiry}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ConfirmUploadView(APIView):
    """Confirm an upload and create a new DocumentVersion."""

    permission_classes = [DocumentPermission]

    def post(self, request):
        serializer = ConfirmUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        s3_key = serializer.validated_data["s3_key"]
        checklist_item_id = serializer.validated_data["checklist_item_id"]

        if not _is_configured():
            return Response(
                {
                    "error": "S3 not configured",
                    "detail": "AWS_S3_BUCKET_NAME is not set",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            checklist_item = LandDocumentChecklistItem.objects.select_related(
                "land"
            ).get(id=checklist_item_id, is_deleted=False)
        except LandDocumentChecklistItem.DoesNotExist:
            return Response(
                {"error": "Checklist item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not check_object_exists(s3_key):
            return Response(
                {"error": "Object not found in S3", "detail": f"Key: {s3_key}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        latest_version = (
            checklist_item.versions.filter(is_deleted=False)
            .order_by("-version_number")
            .first()
        )
        new_version_number = (
            (latest_version.version_number + 1) if latest_version else 1
        )

        with transaction.atomic():
            version = DocumentVersion.objects.create(
                checklist_item=checklist_item,
                version_number=new_version_number,
                s3_key=s3_key,
                original_filename=s3_key.split("/")[-1],
                content_type=request.data.get(
                    "content_type", "application/octet-stream"
                ),
                uploaded_by=request.user,
                created_by=request.user,
                updated_by=request.user,
            )

        response_serializer = ConfirmUploadResponseSerializer(
            {"version": version}, context={"request": request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PresignedDownloadView(APIView):
    """Generate a presigned URL for downloading a document."""

    permission_classes = [DocumentPermission]

    def post(self, request):
        serializer = PresignedDownloadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        version_id = serializer.validated_data["version_id"]

        try:
            version = DocumentVersion.objects.select_related(
                "checklist_item__land"
            ).get(id=version_id, is_deleted=False)
        except DocumentVersion.DoesNotExist:
            return Response(
                {"error": "Document version not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not version.s3_key:
            return Response(
                {"error": "No file associated with this version"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _is_configured():
            return Response(
                {
                    "error": "S3 not configured",
                    "detail": "AWS_S3_BUCKET_NAME is not set",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            download_url, expiry = generate_presigned_download_url(version.s3_key)
        except S3ServiceError as e:
            return Response(
                {"error": "Failed to generate download URL", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_serializer = PresignedDownloadResponseSerializer(
            {"download_url": download_url, "expiry_seconds": expiry}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
