from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.documents.views import (
    ConfirmUploadView,
    DocumentVersionViewSet,
    IdentityDocumentViewSet,
    LandCompletionStatsView,
    LandDocumentChecklistViewSet,
    PresignedDownloadView,
    PresignedUploadView,
)

router = DefaultRouter()
router.register(
    r"documents/checklist", LandDocumentChecklistViewSet, basename="document-checklist"
)
router.register(
    r"documents/versions", DocumentVersionViewSet, basename="document-version"
)
router.register(
    r"identity-documents", IdentityDocumentViewSet, basename="identity-document"
)

urlpatterns = [
    path(
        "documents/presigned-upload",
        PresignedUploadView.as_view(),
        name="presigned-upload",
    ),
    path(
        "documents/confirm-upload",
        ConfirmUploadView.as_view(),
        name="confirm-upload",
    ),
    path(
        "documents/presigned-download",
        PresignedDownloadView.as_view(),
        name="presigned-download",
    ),
    path(
        "documents/completion-stats",
        LandCompletionStatsView.as_view(),
        name="completion-stats",
    ),
] + router.urls
