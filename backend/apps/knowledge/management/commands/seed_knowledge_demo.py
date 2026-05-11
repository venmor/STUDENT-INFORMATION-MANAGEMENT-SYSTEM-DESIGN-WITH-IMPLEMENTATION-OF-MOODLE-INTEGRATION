from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.knowledge.services import seed_demo_knowledge_sources


class Command(BaseCommand):
    help = "Seed safe local institutional knowledge sources for Phase 4.1 retrieval testing."

    def handle(self, *args, **options):
        sources = seed_demo_knowledge_sources()
        self.stdout.write(self.style.SUCCESS("Knowledge demo sources are ready."))
        self.stdout.write(f"sources: {len(sources)}")
        self.stdout.write("Demo sources are local verification text, not official institutional policy.")
