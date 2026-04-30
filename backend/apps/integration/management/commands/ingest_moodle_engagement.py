from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from apps.integration.services import MoodleEngagementError, MoodleEngagementService


class Command(BaseCommand):
    help = (
        "Ingest Moodle engagement snapshots for mapped SIS users and course sections."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--section-id", help="Limit ingestion to one SIS course section UUID."
        )
        parser.add_argument("--user-id", help="Limit ingestion to one SIS user id.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Inspect Moodle data without creating snapshots.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of mapped Moodle courses to inspect.",
        )
        parser.add_argument(
            "--since",
            help="Only store snapshots with Moodle access at or after this ISO datetime.",
        )

    def handle(self, *args, **options):
        since = self._parse_since(options.get("since"))
        try:
            run = MoodleEngagementService().ingest(
                section_id=options.get("section_id"),
                user_id=options.get("user_id"),
                dry_run=options["dry_run"],
                limit=options["limit"],
                since=since,
            )
        except MoodleEngagementError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Moodle engagement ingestion complete: "
                f"status={run.status} "
                f"dry_run={run.dry_run} "
                f"courses_inspected={run.courses_inspected} "
                f"users_inspected={run.users_inspected} "
                f"snapshots_created={run.snapshots_created} "
                f"snapshots_updated={run.snapshots_updated} "
                f"skipped_unmapped_users={run.skipped_unmapped_users} "
                f"failures={run.failure_count}"
            )
        )
        if run.last_error:
            self.stdout.write(f"Last safe error: {run.last_error}")

    def _parse_since(self, value: str | None):
        if not value:
            return None
        parsed = parse_datetime(value)
        if parsed is None:
            raise CommandError(
                "--since must be an ISO datetime, for example 2026-04-30T00:00:00Z."
            )
        return parsed
