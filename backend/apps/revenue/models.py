"""Models for the Revenue module, handling Officer profiles and Government Workflows."""

from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel  # Fix 1: Mandatory Base Class


class OfficerDesignation(models.TextChoices):
    DC = "DC", "District Commissioner"
    AC = "AC", "Assistant Commissioner"
    TAHSILDAR = "TAHSILDAR", "Tahsildar"
    DEPUTY_TAHSILDAR = "DEPUTY_TAHSILDAR", "Deputy Tahsildar"
    VA = "VA", "Village Accountant"
    RI = "RI", "Revenue Inspector"
    ADLR = "ADLR", "Assistant Director of Land Records"
    DDLR = "DDLR", "Deputy Director of Land Records"


class WorkflowKind(models.TextChoices):
    MUTATION = "MUTATION", "Mutation"
    PHODI = "PHODI", "Phodi"
    TIPPANI = "TIPPANI", "Tippani"
    RTC_CORRECTION = "RTC_CORRECTION", "RTC Correction"
    CONVERSION = "CONVERSION", "Conversion"


class WorkflowStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not started"
    APPLIED = "APPLIED", "Applied"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    ON_HOLD = "ON_HOLD", "On hold"


class Officer(BaseModel):  # Fix 1: UUIDv7 + Audit + SoftDelete
    name = models.CharField(max_length=255)
    designation = models.CharField(
        max_length=50, choices=OfficerDesignation.choices, default=OfficerDesignation.VA
    )
    # Fix 7: Explicit related_name
    district = models.ForeignKey(
        "geography.District",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revenue_officers",
    )
    taluk = models.ForeignKey(
        "geography.Taluk",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revenue_officers",
    )
    internal_user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revenue_officer_profile",
    )

    class Meta:  # Fix 6: Required Meta class
        ordering = ["name"]
        verbose_name = "Revenue Officer"
        verbose_name_plural = "Revenue Officers"

    def __str__(self):
        return f"{self.name} ({self.get_designation_display()})"


class GovernmentWorkflow(BaseModel):  # Fix 1: Correct Base Class
    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,  # Fix 2: Changed from CASCADE to PROTECT
        related_name="government_workflows",
    )
    kind = models.CharField(max_length=64, choices=WorkflowKind.choices)
    status = models.CharField(
        max_length=64,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.NOT_STARTED,
    )
    applied_on = models.DateField(null=True, blank=True)  # Minor 2: Removed default
    officer_handling = models.ForeignKey(
        Officer,
        on_delete=models.PROTECT,
        related_name="workflows",
        null=True,
        blank=True,
    )
    remarks = models.TextField(blank=True)  # Minor 1: Removed null=True

    @property
    def days_pending(self):
        if not self.applied_on:
            return 0
        return (timezone.now().date() - self.applied_on).days

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Government workflow"
        verbose_name_plural = "Government workflows"
        constraints = [
            models.UniqueConstraint(
                fields=["land", "kind"], name="unique_active_workflow_per_land"
            )
        ]

    def __str__(self) -> str:
        return f"{self.land.land_id} — {self.kind}"
