from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.constants import RoleCode
from apps.calendar.services import seed_demo_events


class Command(BaseCommand):
    help = "Create safe local demo academic calendar events for Step 3.5D."

    def handle(self, *args, **options):
        actor = get_user_model().objects.filter(primary_role=RoleCode.ADMIN, is_active=True).order_by("id").first()
        result = seed_demo_events(actor=actor)
        self.stdout.write(self.style.SUCCESS(f"Academic calendar demo seed complete: {result.created} created, {result.updated} updated."))
