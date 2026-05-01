from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.knowledge.services import ingest_knowledge_base


class Command(BaseCommand):
    help = "Chunk, embed, and upsert ready institutional knowledge sources into the configured vector store."

    def add_arguments(self, parser):
        parser.add_argument("--source-id", help="Limit ingestion to a source UUID.")
        parser.add_argument("--source-type", default="", help="Limit ingestion to a knowledge source type.")
        parser.add_argument("--rebuild", action="store_true", help="Delete existing chunks for each selected source before ingesting.")
        parser.add_argument("--dry-run", action="store_true", help="Calculate chunks without writing chunks or vector records.")
        parser.add_argument("--limit", type=int, help="Maximum number of sources to process.")

    def handle(self, *args, **options):
        run = ingest_knowledge_base(
            source_id=options.get("source_id"),
            source_type=options.get("source_type") or "",
            rebuild=options["rebuild"],
            dry_run=options["dry_run"],
            limit=options.get("limit"),
        )
        if run.status == "FAILED":
            raise CommandError(run.last_error or "Knowledge ingestion failed.")
        self.stdout.write(self.style.SUCCESS("Knowledge ingestion complete"))
        self.stdout.write(f"run id: {run.id}")
        self.stdout.write(f"status: {run.status}")
        self.stdout.write(f"sources processed: {run.sources_processed}")
        self.stdout.write(f"chunks created: {run.chunks_created}")
        self.stdout.write(f"chunks upserted: {run.chunks_upserted}")
        self.stdout.write(f"failures: {run.failure_count}")
        if run.last_error:
            self.stdout.write(f"last error: {run.last_error}")
