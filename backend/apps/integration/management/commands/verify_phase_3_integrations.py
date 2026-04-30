from django.conf import settings
from django.core.management.base import BaseCommand

from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleUserMap,
)


class Command(BaseCommand):
    help = "Print a local Phase 3 Moodle integration readiness report without calling live Moodle."

    def handle(self, *args, **options):
        pending_events = IntegrationOutboxEvent.objects.filter(
            status=IntegrationEventStatus.PENDING
        ).count()
        failed_events = IntegrationOutboxEvent.objects.filter(
            status=IntegrationEventStatus.FAILED
        ).count()
        latest_run = MoodleEngagementIngestionRun.objects.order_by(
            "-started_at"
        ).first()

        self.stdout.write("Phase 3 integration readiness")
        self.stdout.write(
            f"Moodle REST config: {self._present(settings.MOODLE_BASE_URL and settings.MOODLE_WS_TOKEN)}"
        )
        self.stdout.write(f"LTI config: {self._present(self._has_lti_config())}")
        self.stdout.write(f"Moodle user mappings: {MoodleUserMap.objects.count()}")
        self.stdout.write(f"Moodle course mappings: {MoodleCourseMap.objects.count()}")
        self.stdout.write(f"Pending outbox events: {pending_events}")
        self.stdout.write(f"Failed outbox events: {failed_events}")
        if latest_run is None:
            self.stdout.write("Latest engagement ingestion: none")
        else:
            self.stdout.write(
                "Latest engagement ingestion: "
                f"{latest_run.status} "
                f"courses={latest_run.courses_inspected} "
                f"users={latest_run.users_inspected} "
                f"snapshots={latest_run.snapshots_created + latest_run.snapshots_updated} "
                f"failures={latest_run.failure_count}"
            )
        self.stdout.write("Live Moodle calls: not performed")

    def _has_lti_config(self) -> bool:
        has_key_material = bool(
            settings.LTI_PRIVATE_KEY
            or settings.LTI_PRIVATE_KEY_FILE
            or settings.LTI_PUBLIC_KEY
            or settings.LTI_PUBLIC_KEY_FILE
        )
        return bool(
            settings.LTI_CLIENT_ID
            and settings.LTI_DEPLOYMENT_ID
            and settings.LTI_PLATFORM_ISSUER_ALLOWLIST
            and has_key_material
        )

    def _present(self, value) -> str:
        return "present" if value else "missing"
