from django.core.management.base import BaseCommand

from apps.atrisk.services import auto_close_resolved_alerts, run_at_risk_engine


class Command(BaseCommand):
    help = "Run the at-risk student insight engine (same logic as nightly Celery task)."

    def handle(self, *args, **options):
        self.stdout.write("Starting at-risk engine...")

        # Step 1: Auto-close resolved alerts
        closed = auto_close_resolved_alerts()
        self.stdout.write(f"  Auto-closed {closed} resolved alert(s).")

        # Step 2: Process all active students
        stats = run_at_risk_engine()
        self.stdout.write(f"  Students processed: {stats['students_processed']}")
        self.stdout.write(f"  Alerts created: {stats['alerts_created']}")
        self.stdout.write(f"  Alerts updated: {stats['alerts_updated']}")
        self.stdout.write(f"  Alerts closed: {stats['alerts_closed']}")
        self.stdout.write(f"  Errors: {stats['errors']}")

        self.stdout.write(self.style.SUCCESS("At-risk engine run complete."))
