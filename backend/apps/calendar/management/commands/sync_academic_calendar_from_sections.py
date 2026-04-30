from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.calendar.services import sync_events_from_course_sections


class Command(BaseCommand):
    help = "Create or update academic calendar events from course-section registration and drop dates."

    def handle(self, *args, **options):
        result = sync_events_from_course_sections()
        self.stdout.write(self.style.SUCCESS(f"Academic calendar section sync complete: {result.created} created, {result.updated} updated."))
