from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.analytics.services import run_analytics_etl


class Command(BaseCommand):
    help = "Run the Phase 4.1 analytics ETL over existing SIS and stored Moodle engagement data."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Calculate values without writing analytics snapshots.")
        parser.add_argument("--student-id", help="Limit ETL to one student UUID.")
        parser.add_argument("--academic-year", default="", help="Academic year label for snapshots.")
        parser.add_argument("--semester", default="", help="Semester label for snapshots.")
        parser.add_argument("--limit", type=int, help="Maximum number of active students to process.")

    def handle(self, *args, **options):
        run = run_analytics_etl(
            dry_run=options["dry_run"],
            student_id=options.get("student_id"),
            academic_year=options.get("academic_year") or "",
            semester=options.get("semester") or "",
            limit=options.get("limit"),
        )
        self.stdout.write(self.style.SUCCESS("Analytics ETL complete"))
        self.stdout.write(f"run id: {run.id}")
        self.stdout.write(f"status: {run.status}")
        self.stdout.write(f"students processed: {run.students_processed}")
        self.stdout.write(f"snapshots created: {run.snapshots_created}")
        self.stdout.write(f"snapshots updated: {run.snapshots_updated}")
        self.stdout.write(f"moodle snapshots used: {run.moodle_snapshots_used}")
        self.stdout.write(f"failures: {run.failure_count}")
        self.stdout.write(f"dry run: {'yes' if run.dry_run else 'no'}")
        if run.last_error:
            self.stdout.write(f"last error: {run.last_error}")
