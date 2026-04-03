"""Minimal geography rows for local demos and manual UI testing (idempotent)."""

from django.core.management.base import BaseCommand

from apps.geography.models import District, Hobli, Taluk, Village


class Command(BaseCommand):
    help = (
        "Create one District → Taluk → Hobli → Village chain for Karnataka. "
        "Safe to run multiple times (get_or_create)."
    )

    def handle(self, *args, **options):
        d, _ = District.objects.get_or_create(
            name="Demo District (Bengaluru Rural)",
            defaults={"state": "Karnataka"},
        )
        t, _ = Taluk.objects.get_or_create(name="Demo Taluk (Devanahalli)", district=d)
        h, _ = Hobli.objects.get_or_create(name="Demo Hobli", taluk=t)
        v, _ = Village.objects.get_or_create(name="Demo Village (Budigere)", hobli=h)
        self.stdout.write(
            self.style.SUCCESS(
                f"Geography ready: village pk={v.pk} — use this in Land create cascade."
            )
        )
