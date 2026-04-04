import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from uuid_utils import uuid7 as _uuid7


def generate_uuid7() -> uuid.UUID:
    """Return a stdlib ``uuid.UUID`` instance containing a UUIDv7 value."""
    return uuid.UUID(str(_uuid7()))


class ActiveManager(models.Manager):
    """Default manager that filters out soft-deleted rows."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditedModel(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    class Meta:
        abstract = True


class BaseModel(AuditedModel, SoftDeleteModel):
    """Combines Audited + SoftDelete — the standard base for all domain models.

    Primary key is **UUIDv7** (time-ordered, globally unique, no sequence
    contention). Geography, User, and AuditLog keep integer PKs.
    """

    id = models.UUIDField(primary_key=True, default=generate_uuid7, editable=False)

    class Meta:
        abstract = True
