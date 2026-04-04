from django.urls import path

from apps.documents.views import (
    ConfirmUploadView,
    DocumentVersionViewSet,
    LandDocumentChecklistViewSet,
    PresignedDownloadView,
    PresignedUploadView,
)

urlpatterns = [
    path("documents/presigned-upload", PresignedUploadView.as_view(), name="presigned-upload",),
    path("documents/confirm-upload", ConfirmUploadView.as_view(), name="confirm-upload",),
    path("documents/presigned-download", PresignedDownloadView.as_view(), name="presigned-download",),
    path("documents/checklist", LandDocumentChecklistViewSet.as_view(), name="document-checklist-list",),
    path("documents/checklist/<str:land_id>", LandDocumentChecklistViewSet.as_view(), name="document-checklist-by-land",),
    path("documents/versions/<str:checklist_item_id>", DocumentVersionViewSet.as_view(), name="document-versions",),
    path("documents/versions/delete/<str:version_id>", DocumentVersionViewSet.as_view(), name="document-version-delete",),
]
