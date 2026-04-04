"""
Legal & litigation domain — land-anchored master file (PRD §3, HLD §3.2).

This module is a **scaffold**: `LegalCase` is the minimum anchor. Person 1 extends
with hearings, POA, advocates, court enums, and APIs per ASSIGNMENT_PERSON_01_LEGAL.md.
"""

from django.db import models

from apps.core.models import BaseModel


class LegalCase(BaseModel):
    """
    One litigation / civil matter tied to a single land file.

    Expand with party role, court level, case type, stages, advocate M2M, etc.
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

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Legal Case"
        verbose_name_plural = "Legal Cases"

    def __str__(self) -> str:
        ref = self.case_number or f"id={self.pk}"
        return f"{ref} — {self.land.land_id}"
