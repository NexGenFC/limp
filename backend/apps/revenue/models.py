from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# LIMP standard base models
from apps.core.models import AuditedModel, SoftDeleteModel


class OfficerDesignation(models.TextChoices):
    DC = "DC", _("District Commissioner")
    AC = "AC", _("Assistant Commissioner")
    TAHSILDAR = "TAHSILDAR", _("Tahsildar")
    DEPUTY_TAHSILDAR = "DEPUTY_TAHSILDAR", _("Deputy Tahsildar")
    VA = "VA", _("Village Accountant")
    RI = "RI", _("Revenue Inspector")
    ADLR = "ADLR", _("Assistant Director of Land Records")
    DDLR = "DDLR", _("Deputy Director of Land Records")


class WorkflowKind(models.TextChoices):
    MUTATION = "MUTATION", _("Mutation")
    PHODI = "PHODI", _("Phodi")
    TIPPANI = "TIPPANI", _("Tippani")
    RTC_CORRECTION = "RTC_CORRECTION", _("RTC Correction")
    CONVERSION = "CONVERSION", _("Conversion")


class WorkflowStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", _("Not started")
    APPLIED = "APPLIED", _("Applied")
    IN_PROGRESS = "IN_PROGRESS", _("In progress")
    COMPLETED = "COMPLETED", _("Completed")
    ON_HOLD = "ON_HOLD", _("On hold")


class Officer(AuditedModel, SoftDeleteModel):
    """Reference data for government officers (§3.1)"""

    name = models.CharField(max_length=255)
    designation = models.CharField(
        max_length=50, choices=OfficerDesignation.choices, default=OfficerDesignation.VA
    )
    # Link to geography (Normalization §3.1 & §4.3)
    district = models.ForeignKey(
        "geography.District", on_delete=models.SET_NULL, null=True, blank=True
    )
    taluk = models.ForeignKey(
        "geography.Taluk", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Optional link to internal user
    internal_user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revenue_officer_profile",
    )

    def __str__(self):
        return f"{self.name} ({self.get_designation_display()})"


class GovernmentWorkflow(AuditedModel, SoftDeleteModel):
    """Workflow instances per land file (§3.2)"""

    land = models.ForeignKey(
        "land.LandFile", on_delete=models.CASCADE, related_name="government_workflows"
    )
    kind = models.CharField(max_length=64, choices=WorkflowKind.choices)
    status = models.CharField(
        max_length=64,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.NOT_STARTED,
    )
    applied_on = models.DateField(default=timezone.now, null=True, blank=True)

    # Officer handling the case (§3.2)
    officer_handling = models.ForeignKey(
        Officer,
        on_delete=models.PROTECT,
        related_name="workflows",
        null=True,  # Allowed null initially if not assigned
        blank=True,
    )

    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Government workflow")
        verbose_name_plural = _("Government workflows")
        # CRITICAL: Keep this for CockroachDB compatibility as per brief §0.8
        constraints = [
            models.UniqueConstraint(
                fields=["land", "kind"],
                condition=models.Q(is_deleted=False),
                name="revenue_govworkflow_unique_land_kind_active",
            ),
        ]

    @property
    def days_pending(self):
        """Logic requirement: Today minus applied_on (§3.2)"""
        if not self.applied_on:
            return 0
        return (timezone.now().date() - self.applied_on).days

    def __str__(self) -> str:
        return f"{self.land.land_id} — {self.kind}"
