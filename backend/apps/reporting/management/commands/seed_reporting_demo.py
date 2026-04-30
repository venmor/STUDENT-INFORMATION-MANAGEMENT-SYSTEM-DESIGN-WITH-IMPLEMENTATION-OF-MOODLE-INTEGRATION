from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.constants import RoleCode
from apps.academics.models import CourseSection
from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event
from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.notifications.models import NotificationCategory, NotificationSeverity
from apps.notifications.services import create_notification
from apps.students.models import StudentProfile


class Command(BaseCommand):
    help = "Create safe local demo data for the Step 3.5E Admin Reporting Dashboard."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="DemoPass123!",
            help="Password applied to demo accounts created by seed_demo_sis. Default: DemoPass123!",
        )

    def handle(self, *args, **options):
        call_command("seed_demo_sis", password=options["password"], verbosity=0)
        call_command("seed_academic_calendar_demo", verbosity=0)
        call_command("seed_audit_activity_demo", verbosity=0)

        user_model = get_user_model()
        admin = user_model.objects.filter(username="admin.demo", primary_role=RoleCode.ADMIN).first()
        student = StudentProfile.objects.select_related("user").filter(student_number="2026/CS/001").first()
        section = CourseSection.objects.select_related("course").filter(course__course_code="CSC410", section_code="A1").first()

        created_outbox = self._ensure_reporting_outbox_events()
        created_maps = self._ensure_moodle_mappings(student=student, section=section)
        created_engagement = self._ensure_engagement_run(student=student, section=section)
        created_notifications = self._ensure_admin_notifications(admin)
        created_audit = self._ensure_reporting_audit(admin)

        self.stdout.write(
            self.style.SUCCESS(
                "Reporting demo seed complete: "
                f"outbox={created_outbox} "
                f"mappings={created_maps} "
                f"engagement={created_engagement} "
                f"notifications={created_notifications} "
                f"audit={created_audit}"
            )
        )

    def _ensure_reporting_outbox_events(self) -> int:
        created = 0
        demo_events = [
            {
                "event_type": "USER_SYNC_REQUESTED",
                "status": IntegrationEventStatus.PENDING,
                "payload": {"reportingDemoKey": "pending-user-sync", "safeRecord": "admin.demo"},
            },
            {
                "event_type": "COURSE_SYNC_REQUESTED",
                "status": IntegrationEventStatus.PROCESSED,
                "payload": {"reportingDemoKey": "processed-course-sync", "safeRecord": "CSC410-A1"},
                "processed_at": timezone.now(),
            },
            {
                "event_type": "GRADE_SYNC_REQUESTED",
                "status": IntegrationEventStatus.FAILED,
                "payload": {"reportingDemoKey": "failed-grade-sync", "safeRecord": "CSC410-A1"},
                "attempts": 2,
                "last_error": "Demo Moodle grade sync failure for reporting dashboard.",
                "last_attempt_at": timezone.now(),
            },
        ]
        for event in demo_events:
            if IntegrationOutboxEvent.objects.filter(payload__reportingDemoKey=event["payload"]["reportingDemoKey"]).exists():
                continue
            IntegrationOutboxEvent.objects.create(**event)
            created += 1
        return created

    def _ensure_moodle_mappings(self, *, student: StudentProfile | None, section: CourseSection | None) -> int:
        created = 0
        if (
            student is not None
            and not MoodleUserMap.objects.filter(user=student.user).exists()
            and not MoodleUserMap.objects.filter(moodle_user_id=95001).exists()
        ):
            MoodleUserMap.objects.create(user=student.user, moodle_user_id=95001, moodle_username=student.user.username)
            created += 1
        if (
            section is not None
            and not MoodleCourseMap.objects.filter(section=section).exists()
            and not MoodleCourseMap.objects.filter(moodle_course_id=98001).exists()
        ):
            MoodleCourseMap.objects.create(
                section=section,
                moodle_course_id=98001,
                moodle_shortname=f"{section.course.course_code}-{section.section_code}",
                moodle_category_id=1,
            )
            created += 1
        return created

    def _ensure_engagement_run(self, *, student: StudentProfile | None, section: CourseSection | None) -> int:
        if MoodleEngagementIngestionRun.objects.filter(summary_payload__reportingDemo=True).exists():
            return 0
        run = MoodleEngagementIngestionRun.objects.create(
            status=MoodleEngagementIngestionStatus.PARTIAL,
            completed_at=timezone.now(),
            courses_inspected=1,
            users_inspected=1,
            snapshots_created=1,
            failure_count=1,
            last_error="Demo reporting ingestion warning.",
            summary_payload={"reportingDemo": True},
        )
        if student is not None and section is not None:
            MoodleEngagementSnapshot.objects.create(
                run=run,
                user=student.user,
                student=student,
                section=section,
                moodle_user_id=95001,
                moodle_course_id=98001,
                moodle_course_last_access_at=timezone.now(),
                collected_at=timezone.now(),
            )
        return 1

    def _ensure_admin_notifications(self, admin) -> int:
        if admin is None:
            return 0
        before = admin.notifications.count()
        create_notification(
            recipient=admin,
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.WARNING,
            title="Reporting demo review",
            message="Safe demo notification for the admin reporting dashboard.",
            action_label="Open Reports",
            action_url="/admin/reports",
            source_type="AdminReportDemo",
            source_id="reporting-demo-notification",
        )
        return admin.notifications.count() - before

    def _ensure_reporting_audit(self, admin) -> int:
        if self._reporting_audit_exists():
            return 0
        record_audit_event(
            actor=admin,
            category=AuditCategory.SYSTEM,
            action="ADMIN_REPORT_DEMO_SEEDED",
            summary="Safe reporting dashboard demo data was seeded locally.",
            target_type="AdminReportDemo",
            target_id="reporting-demo",
            severity=AuditSeverity.INFO,
            metadata={"reportingDemo": True},
        )
        return 1

    def _reporting_audit_exists(self) -> bool:
        from apps.audit.models import AuditEvent

        return AuditEvent.objects.filter(action="ADMIN_REPORT_DEMO_SEEDED", target_id="reporting-demo").exists()
