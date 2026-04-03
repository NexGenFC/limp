import datetime

from django.db import models

from apps.core.models import BaseModel
from apps.geography.models import Village


def _next_land_id() -> str:
    year = datetime.date.today().year
    prefix = f"LIMP-{year}-"
    last = (
        LandFile.all_objects.filter(land_id__startswith=prefix)
        .order_by("-land_id")
        .values_list("land_id", flat=True)
        .first()
    )
    if last:
        seq = int(last.split("-")[-1]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


class LandClassification(models.TextChoices):
    AGRICULTURAL = "AGRICULTURAL", "Agricultural"
    CONVERTED = "CONVERTED", "Converted"
    APPROVED_SITE = "APPROVED_SITE", "Approved Site"


class LandStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    UNDER_NEGOTIATION = "UNDER_NEGOTIATION", "Under Negotiation"
    COMMITTED = "COMMITTED", "Committed"
    CLOSED = "CLOSED", "Closed"


class LandFile(BaseModel):
    land_id = models.CharField(
        max_length=32, unique=True, editable=False, db_index=True
    )
    village = models.ForeignKey(
        Village, related_name="land_files", on_delete=models.PROTECT
    )
    survey_number = models.CharField(max_length=64)
    hissa = models.CharField(max_length=64, blank=True)
    extent_acres = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    extent_guntas = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    extent_sqft = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    classification = models.CharField(
        max_length=32,
        choices=LandClassification.choices,
        default=LandClassification.AGRICULTURAL,
    )
    status = models.CharField(
        max_length=32,
        choices=LandStatus.choices,
        default=LandStatus.ACTIVE,
    )
    proposed_by = models.ForeignKey(
        "users.User",
        related_name="proposed_land_files",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    investment_min = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    investment_max = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Land File"
        verbose_name_plural = "Land Files"

    def __str__(self) -> str:
        return f"{self.land_id} — {self.village}"

    def save(self, *args, **kwargs):
        if not self.land_id:
            self.land_id = _next_land_id()
        super().save(*args, **kwargs)
