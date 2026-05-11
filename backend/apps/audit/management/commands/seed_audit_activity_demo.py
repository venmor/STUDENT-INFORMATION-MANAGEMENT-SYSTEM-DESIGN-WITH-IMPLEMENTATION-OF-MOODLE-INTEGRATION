from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditCategory, AuditEvent, AuditSeverity
from apps.audit.services import record_audit_event


class Command(BaseCommand):
    help = "Create safe local demo audit activity for the Step 3.5C admin activity viewer."

    def handle(self, *args, **options):
        user_model = get_user_model()
        actor = user_model.objects.filter(primary_role=RoleCode.ADMIN, is_active=True).order_by("id").first()
        demo_events = [
            {
                "category": AuditCategory.USER,
                "action": "USER_CREATED",
                "summary": "Demo user administration activity recorded for local audit viewer testing.",
                "target_type": "User",
                "target_id": "audit-demo-user",
                "severity": AuditSeverity.SUCCESS,
                "metadata": {"demo": True, "recordType": "user"},
            },
            {
                "category": AuditCategory.MOODLE,
                "action": "MOODLE_SYNC_FAILED",
                "summary": "Demo Moodle sync failure recorded without live Moodle.",
                "target_type": "IntegrationOutboxEvent",
                "target_id": "audit-demo-moodle",
                "severity": AuditSeverity.ERROR,
                "metadata": {"demo": True, "eventType": "GRADE_SYNC_REQUESTED", "safeError": "Demo invalid JSON response."},
            },
            {
                "category": AuditCategory.NOTIFICATION,
                "action": "NOTIFICATION_READ",
                "summary": "Demo notification read activity recorded for local audit viewer testing.",
                "target_type": "Notification",
                "target_id": "audit-demo-notification",
                "severity": AuditSeverity.INFO,
                "metadata": {"demo": True, "category": "SYSTEM"},
            },
            {
                "category": AuditCategory.LTI,
                "action": "LTI_LAUNCH_CREATED",
                "summary": "Demo safe LTI launch session activity recorded without raw launch tokens.",
                "target_type": "LtiLaunchSession",
                "target_id": "audit-demo-lti",
                "severity": AuditSeverity.INFO,
                "metadata": {"demo": True, "toolSlug": "advising-dashboard", "mappedUser": True, "mappedSection": True},
            },
            {
                "category": AuditCategory.SYSTEM,
                "action": "SYSTEM_HEALTH_CHECK",
                "summary": "Demo system governance event recorded for local audit viewer testing.",
                "target_type": "System",
                "target_id": "audit-demo-system",
                "severity": AuditSeverity.WARNING,
                "metadata": {"demo": True, "check": "configuration-readiness"},
            },
            {
                "category": AuditCategory.AI,
                "action": "AI_AUDIT_PLACEHOLDER",
                "summary": "AI audit placeholder category reserved; no AI workflow was executed.",
                "target_type": "Roadmap",
                "target_id": "audit-demo-ai-placeholder",
                "severity": AuditSeverity.INFO,
                "metadata": {"demo": True, "placeholderOnly": True},
            },
        ]

        created = 0
        for event in demo_events:
            if AuditEvent.objects.filter(target_id=event["target_id"], action=event["action"]).exists():
                continue
            record_audit_event(actor=actor, **event)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} Step 3.5C demo audit events."))
