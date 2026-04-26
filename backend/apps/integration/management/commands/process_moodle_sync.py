from django.core.management.base import BaseCommand, CommandError

from apps.integration.models import IntegrationEventStatus, IntegrationOutboxEvent
from apps.integration.services import is_moodle_sync_configured, process_outbox_event


class Command(BaseCommand):
    help = "Process pending or failed Moodle sync events from the integration outbox."

    def add_arguments(self, parser):
        parser.add_argument("--failed", action="store_true", help="Include failed events for retry.")
        parser.add_argument("--event-id", help="Process only the specified outbox event UUID.")
        parser.add_argument("--limit", type=int, default=0, help="Maximum number of events to process.")

    def handle(self, *args, **options):
        if not is_moodle_sync_configured():
            raise CommandError("MOODLE_BASE_URL and MOODLE_WS_TOKEN must be configured before processing Moodle sync.")

        event_id = options.get("event_id")
        include_failed = options["failed"]
        limit = options["limit"]

        if event_id:
            queryset = IntegrationOutboxEvent.objects.filter(pk=event_id)
        else:
            statuses = [IntegrationEventStatus.PENDING]
            if include_failed:
                statuses.append(IntegrationEventStatus.FAILED)
            queryset = IntegrationOutboxEvent.objects.filter(status__in=statuses).order_by("created_at", "id")
            if limit:
                queryset = queryset[:limit]

        processed = 0
        failed = 0
        for event in queryset:
            if process_outbox_event(event.id):
                processed += 1
            else:
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"Moodle sync processing complete: processed={processed} failed={failed}"))
