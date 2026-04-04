"""
Revenue & government workflow — land-anchored (PRD §5, HLD).

Scaffold: one row per workflow *kind* per land is a common pattern; Person 2 may
add officer FKs, pending days, remarks, and split reference tables.
"""

from django.db import models

from apps.core.models import BaseModel


class WorkflowKind(models.TextChoices):
    """Expand to match Karnataka operations (mutation, phodi, …)."""

    MUTATION = "MUTATION", "Mutation"
    PHODI = "PHODI", "Phodi"
    TIPPANI = "TIPPANI", "Tippani"
    RTC_CORRECTION = "RTC_CORRECTION", "RTC correction"
    CONVERSION = "CONVERSION", "Conversion"


class WorkflowStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not started"
    APPLIED = "APPLIED", "Applied"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    ON_HOLD = "ON_HOLD", "On hold"


class GovernmentWorkflow(BaseModel):
    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,
        related_name="government_workflows",
    )
    kind = models.CharField(max_length=64, choices=WorkflowKind.choices)
    status = models.CharField(
        max_length=64,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.NOT_STARTED,
    )
    applied_on = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Government workflow"
        verbose_name_plural = "Government workflows"
        constraints = [
            models.UniqueConstraint(
                fields=["land", "kind"],
                condition=models.Q(is_deleted=False),
                name="revenue_govworkflow_unique_land_kind_active",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.land.land_id} — {self.kind}"
