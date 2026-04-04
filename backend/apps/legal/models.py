"""
Legal & litigation domain — land-anchored master file (PRD §3, HLD §3.2).
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class CaseType(models.TextChoices):
    OS = "OS", "OS"
    MFA = "MFA", "MFA"
    WP = "WP", "WP"
    CRP = "CRP", "CRP"
    OTHER = "OTHER", "Other"


class PartyRole(models.TextChoices):
    PLAINTIFF = "PLAINTIFF", "Plaintiff"
    DEFENDANT = "DEFENDANT", "Defendant"
    PETITIONER = "PETITIONER", "Petitioner"
    RESPONDENT = "RESPONDENT", "Respondent"


class AdvocateRole(models.TextChoices):
    LEAD = "LEAD", "Lead"
    SUPPORTING = "SUPPORTING", "Supporting"


class POAStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUBMITTED = "SUBMITTED", "Submitted"
    OVERDUE = "OVERDUE", "Overdue"


class LegalCase(BaseModel):
    """
    One litigation / civil matter tied to a single land file.
    """

    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,
        related_name="legal_cases",
    )
    case_number = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        help_text="Court / filing reference when known.",
    )
    title = models.CharField(max_length=255, blank=True)
    case_type = models.CharField(
        max_length=16,
        choices=CaseType.choices,
        blank=True,
        default="",
    )
    court_jurisdiction = models.CharField(max_length=255, blank=True)
    party_role = models.CharField(
        max_length=32,
        choices=PartyRole.choices,
        blank=True,
        default="",
    )
    current_stage = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    assigned_advocates = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="CaseAdvocate",
        through_fields=("case", "advocate"),
        related_name="assigned_cases",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Legal Case"
        verbose_name_plural = "Legal Cases"

    def __str__(self) -> str:
        ref = self.case_number or f"id={self.pk}"
        return f"{ref} — {self.land.land_id}"


class CaseAdvocate(BaseModel):
    case = models.ForeignKey(
        LegalCase,
        on_delete=models.PROTECT,
        related_name="case_advocates",
    )
    advocate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="advocate_cases",
    )
    role = models.CharField(max_length=16, choices=AdvocateRole.choices)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Case advocate"
        verbose_name_plural = "Case advocates"
        constraints = [
            models.UniqueConstraint(
                fields=["case", "advocate"],
                condition=models.Q(is_deleted=False),
                name="legal_caseadvocate_unique_case_advocate_active",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.case_id} — advocate={self.advocate_id} ({self.role})"


class Hearing(BaseModel):
    case = models.ForeignKey(
        LegalCase,
        on_delete=models.PROTECT,
        related_name="hearings",
    )
    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,
        related_name="hearings",
    )
    hearing_date = models.DateField(db_index=True)
    stage_notes = models.TextField(blank=True)
    s3_key = models.CharField(max_length=1024, blank=True)
    outcome = models.TextField(blank=True)

    class Meta:
        ordering = ["hearing_date"]
        verbose_name = "Hearing"


class PlanOfAction(BaseModel):
    hearing = models.OneToOneField(
        Hearing,
        on_delete=models.PROTECT,
        related_name="poa",
    )
    land = models.ForeignKey(
        "land.LandFile",
        on_delete=models.PROTECT,
        related_name="plans_of_action",
    )
    status = models.CharField(
        max_length=16,
        choices=POAStatus.choices,
        default=POAStatus.PENDING,
    )
    deadline = models.DateField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    s3_key = models.CharField(max_length=1024, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Plan of action"
        verbose_name_plural = "Plans of action"

    @classmethod
    def compute_deadline(cls, hearing_date):
        return hearing_date - timedelta(days=2)

    def is_overdue(self) -> bool:
        if self.status == POAStatus.SUBMITTED:
            return False
        if self.deadline is None:
            return False
        return timezone.localdate() > self.deadline

    def save(self, *args, **kwargs):
        if self.deadline is None and self.hearing_id:
            h = self.hearing
            self.deadline = self.compute_deadline(h.hearing_date)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"POA for hearing {self.hearing_id} — {self.status}"
