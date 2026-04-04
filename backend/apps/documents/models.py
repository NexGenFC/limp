"""
Document vault & checklist — land-anchored (PRD §7, HLD §3.3).

Files live in S3; only `s3_key` and metadata here. Person 4 adds presigned
endpoints, confirm-upload flow, and RBAC.
"""

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class DocumentKind(models.TextChoices):
    """Expand as the master checklist grows."""

    RTC = "RTC", "RTC"
    EC = "EC", "Encumbrance certificate"
    PHODI_SKETCH = "PHODI_SKETCH", "Phodi sketch"
    TIPPANI = "TIPPANI", "Tippani"
    GRANT_ORDER = "GRANT_ORDER", "Grant order"
    COURT_CERTIFIED_COPY = "COURT_CERTIFIED_COPY", "Court certified copy"
    OTHER = "OTHER", "Other"


class ChecklistStatus(models.TextChoices):
    CERTIFIED_OBTAINED = "CERTIFIED_OBTAINED", "Certified obtained"
    APPLIED_PENDING = "APPLIED_PENDING", "Applied & pending"
    NOT_APPLICABLE = "NOT_APPLICABLE", "Not applicable"


class LandDocumentChecklistItem(BaseModel):
    """One row per document type per land file (checklist engine)."""

    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,
        related_name="document_checklist_items",
    )
    document_kind = models.CharField(max_length=64, choices=DocumentKind.choices)
    checklist_status = models.CharField(
        max_length=32,
        choices=ChecklistStatus.choices,
        default=ChecklistStatus.APPLIED_PENDING,
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["document_kind"]
        verbose_name = "Land document checklist item"
        verbose_name_plural = "Land document checklist items"
        constraints = [
            models.UniqueConstraint(
                fields=["land", "document_kind"],
                condition=models.Q(is_deleted=False),
                name="documents_checklist_unique_land_kind_active",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.land.land_id} — {self.document_kind}"


class DocumentVersion(BaseModel):
    """Versioned S3 object linked to a checklist row."""

    checklist_item = models.ForeignKey(
        LandDocumentChecklistItem,
        on_delete=models.PROTECT,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField(default=1)
    s3_key = models.CharField(max_length=1024, blank=True)
    original_filename = models.CharField(max_length=512, blank=True)
    content_type = models.CharField(max_length=128, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_versions_uploaded",
    )

    class Meta:
        ordering = ["checklist_item", "-version_number"]
        verbose_name = "Document version"
        verbose_name_plural = "Document versions"

    def __str__(self) -> str:
        return f"v{self.version_number} {self.checklist_item}"
