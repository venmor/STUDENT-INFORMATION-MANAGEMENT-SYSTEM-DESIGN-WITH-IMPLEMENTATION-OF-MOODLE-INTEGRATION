from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.academics.models import CourseSection, Enrollment, GradeRecord, GradeStatus
from apps.accounts.models import User

from .models import IntegrationEventStatus, IntegrationOutboxEvent, MoodleCourseMap, MoodleUserMap


logger = logging.getLogger(__name__)


class MoodleSyncError(Exception):
    """Raised when a Moodle sync operation fails safely."""


@dataclass(frozen=True)
class MoodleUserNameParts:
    firstname: str
    lastname: str


def is_moodle_sync_configured() -> bool:
    return bool(settings.MOODLE_BASE_URL and settings.MOODLE_WS_TOKEN)


def create_sync_event(*, event_type: str, payload: dict[str, Any], auto_process: bool = True) -> IntegrationOutboxEvent:
    event = IntegrationOutboxEvent.objects.create(event_type=event_type, payload=payload)
    if auto_process and is_moodle_sync_configured():
        transaction.on_commit(lambda event_id=event.id: process_outbox_event(event_id))
    return event


def process_outbox_event(event_id) -> bool:
    event = IntegrationOutboxEvent.objects.get(pk=event_id)
    event.attempts += 1
    event.last_attempt_at = timezone.now()
    event.save(update_fields=["attempts", "last_attempt_at"])

    service = MoodleSyncService()
    try:
        service.process_event(event)
    except Exception as exc:
        safe_error = str(exc)
        event.status = IntegrationEventStatus.FAILED
        event.last_error = safe_error
        event.save(update_fields=["status", "last_error"])
        logger.warning("Moodle sync failed for event %s (%s): %s", event.id, event.event_type, safe_error)
        return False

    event.status = IntegrationEventStatus.PROCESSED
    event.last_error = ""
    event.processed_at = timezone.now()
    event.save(update_fields=["status", "last_error", "processed_at"])
    return True


class MoodleSyncService:
    def __init__(self):
        self.base_url = settings.MOODLE_BASE_URL
        self.token = settings.MOODLE_WS_TOKEN
        self.endpoint = f"{self.base_url}/webservice/rest/server.php" if self.base_url else ""
        self.timeout = getattr(settings, "MOODLE_SYNC_TIMEOUT", 10)

    def process_event(self, event: IntegrationOutboxEvent):
        event_type = event.event_type
        payload = event.payload or {}

        if event_type == "USER_SYNC_REQUESTED":
            user = User.objects.get(pk=payload["user_id"])
            action = payload.get("action", "UPSERT")
            self.sync_user(user, action=action)
            return

        if event_type == "COURSE_SYNC_REQUESTED":
            section = CourseSection.objects.select_related("course", "faculty_user").get(pk=payload["section_id"])
            self.sync_section(section)
            return

        if event_type == "ENROLLMENT_SYNC_REQUESTED":
            enrollment = self._resolve_enrollment(payload)
            action = payload.get("action", "ENROLL")
            self.sync_enrollment(enrollment, action=action)
            return

        if event_type == "GRADE_SYNC_REQUESTED":
            grade_record = GradeRecord.objects.select_related("student__user", "section__course", "section__faculty_user").get(
                pk=payload["grade_id"]
            )
            self.sync_grade_record(grade_record)
            return

        raise MoodleSyncError(f"Unsupported Moodle sync event type: {event_type}")

    def sync_user(self, user: User, *, action: str = "UPSERT") -> MoodleUserMap | None:
        if action == "SUSPEND" or not user.is_active:
            mapping = MoodleUserMap.objects.filter(user=user).first() or self.lookup_existing_user_map(
                user,
                create_if_found=True,
            )
            if mapping is None:
                return None
            self._request(
                "core_user_update_users",
                {
                    "users[0][id]": mapping.moodle_user_id,
                    "users[0][email]": user.email,
                    "users[0][firstname]": self._user_name_parts(user).firstname,
                    "users[0][lastname]": self._user_name_parts(user).lastname,
                    "users[0][institution]": settings.MOODLE_INSTITUTION,
                    "users[0][suspended]": 1,
                },
            )
            return mapping

        mapping = MoodleUserMap.objects.filter(user=user).first()
        if mapping is not None:
            self._request(
                "core_user_update_users",
                {
                    "users[0][id]": mapping.moodle_user_id,
                    "users[0][email]": user.email,
                    "users[0][firstname]": self._user_name_parts(user).firstname,
                    "users[0][lastname]": self._user_name_parts(user).lastname,
                    "users[0][institution]": settings.MOODLE_INSTITUTION,
                    "users[0][suspended]": 0,
                },
            )
            mapping.moodle_username = user.username
            mapping.save(update_fields=["moodle_username", "last_synced_at"])
            return mapping

        try:
            self._request(
                "core_user_create_users",
                {
                    "users[0][username]": user.username,
                    "users[0][email]": user.email,
                    "users[0][firstname]": self._user_name_parts(user).firstname,
                    "users[0][lastname]": self._user_name_parts(user).lastname,
                    "users[0][password]": self._generate_temporary_password(),
                    "users[0][institution]": settings.MOODLE_INSTITUTION,
                    "users[0][auth]": "manual",
                    "users[0][idnumber]": str(user.id),
                },
            )
        except MoodleSyncError as exc:
            if not self._looks_like_existing_user_error(exc):
                raise

        mapping = self.lookup_existing_user_map(user, create_if_found=True)
        if mapping is None:
            raise MoodleSyncError("Moodle user creation completed without a user lookup result.")
        return mapping

    def ensure_user_mapping(self, user: User) -> MoodleUserMap:
        mapping = MoodleUserMap.objects.filter(user=user).first()
        if mapping is not None:
            return mapping
        created_mapping = self.sync_user(user, action="UPSERT")
        if created_mapping is None:
            raise MoodleSyncError("The user could not be mapped to Moodle.")
        return created_mapping

    def lookup_existing_user_map(self, user: User, *, create_if_found: bool = False) -> MoodleUserMap | None:
        response_payload = self._request(
            "core_user_get_users",
            {
                "criteria[0][key]": "username",
                "criteria[0][value]": user.username,
            },
        )
        users = response_payload.get("users")
        if not isinstance(users, list):
            raise MoodleSyncError("Moodle user lookup did not return a users list.")
        if not users:
            return None
        found_user = users[0]
        if "id" not in found_user:
            raise MoodleSyncError("Moodle user lookup did not include an id.")
        if create_if_found:
            mapping, _ = MoodleUserMap.objects.update_or_create(
                user=user,
                defaults={
                    "moodle_user_id": int(found_user["id"]),
                    "moodle_username": found_user.get("username", user.username),
                },
            )
            return mapping
        return MoodleUserMap.objects.filter(user=user).first()

    def sync_section(self, section: CourseSection) -> MoodleCourseMap | None:
        if not settings.MOODLE_DEFAULT_CATEGORY_ID:
            raise MoodleSyncError("MOODLE_DEFAULT_CATEGORY_ID is not configured.")

        mapping = MoodleCourseMap.objects.filter(section=section).first()
        shortname = self._build_course_shortname(section)
        fullname = self._build_course_fullname(section)
        shared_fields = {
            "shortname": shortname,
            "fullname": fullname,
            "summary": self._build_course_summary(section),
            "startdate": int(section.registration_opens_at.timestamp()),
            "enddate": int(section.drop_deadline.timestamp()),
        }

        if mapping is None:
            response_payload = self._request(
                "core_course_create_courses",
                {
                    "courses[0][categoryid]": settings.MOODLE_DEFAULT_CATEGORY_ID,
                    "courses[0][shortname]": shortname,
                    "courses[0][fullname]": fullname,
                    "courses[0][summary]": shared_fields["summary"],
                    "courses[0][startdate]": shared_fields["startdate"],
                    "courses[0][enddate]": shared_fields["enddate"],
                },
            )
            if not isinstance(response_payload, list) or not response_payload or "id" not in response_payload[0]:
                raise MoodleSyncError("Moodle course create did not return a course id.")
            created_course = response_payload[0]
            return MoodleCourseMap.objects.create(
                section=section,
                moodle_course_id=int(created_course["id"]),
                moodle_shortname=created_course.get("shortname", shortname),
                moodle_category_id=settings.MOODLE_DEFAULT_CATEGORY_ID,
            )

        self._request(
            "core_course_update_courses",
            {
                "courses[0][id]": mapping.moodle_course_id,
                "courses[0][shortname]": shortname,
                "courses[0][fullname]": fullname,
                "courses[0][summary]": shared_fields["summary"],
                "courses[0][startdate]": shared_fields["startdate"],
                "courses[0][enddate]": shared_fields["enddate"],
            },
        )
        mapping.moodle_shortname = shortname
        mapping.moodle_category_id = settings.MOODLE_DEFAULT_CATEGORY_ID
        mapping.save(update_fields=["moodle_shortname", "moodle_category_id", "last_synced_at"])
        return mapping

    def ensure_course_mapping(self, section: CourseSection) -> MoodleCourseMap:
        mapping = MoodleCourseMap.objects.filter(section=section).first()
        if mapping is not None:
            return mapping
        created_mapping = self.sync_section(section)
        if created_mapping is None:
            raise MoodleSyncError("The section could not be mapped to Moodle.")
        return created_mapping

    def sync_enrollment(self, enrollment: Enrollment, *, action: str = "ENROLL") -> None:
        if action == "ENROLL" and not settings.MOODLE_STUDENT_ROLE_ID:
            raise MoodleSyncError("MOODLE_STUDENT_ROLE_ID is not configured.")

        student_user = enrollment.student.user
        user_map = self.ensure_user_mapping(student_user)
        course_map = self.ensure_course_mapping(enrollment.section)

        if action == "DROP":
            self._request(
                "enrol_manual_unenrol_users",
                {
                    "enrolments[0][userid]": user_map.moodle_user_id,
                    "enrolments[0][courseid]": course_map.moodle_course_id,
                },
            )
            return

        self._request(
            "enrol_manual_enrol_users",
            {
                "enrolments[0][roleid]": settings.MOODLE_STUDENT_ROLE_ID,
                "enrolments[0][userid]": user_map.moodle_user_id,
                "enrolments[0][courseid]": course_map.moodle_course_id,
            },
        )

    def sync_grade_record(self, grade_record: GradeRecord) -> None:
        if grade_record.grade_status != GradeStatus.OFFICIAL:
            raise MoodleSyncError("Only official SIS grades can be synced to Moodle.")
        if grade_record.numeric_score is None:
            raise MoodleSyncError("Step 3.2 supports only numeric official grades for Moodle pass-back.")

        user_map = self.ensure_user_mapping(grade_record.student.user)
        course_map = self.ensure_course_mapping(grade_record.section)

        self._request(
            "gradereport_user_get_grade_items",
            {
                "courseid": course_map.moodle_course_id,
                "userid": user_map.moodle_user_id,
            },
        )

        if not course_map.grade_component or course_map.grade_activity_id is None or course_map.grade_item_number is None:
            raise MoodleSyncError(
                "The Moodle course map has no configured grade target for grade pass-back."
            )

        self._request(
            "core_grades_update_grades",
            {
                "source": settings.MOODLE_GRADE_SOURCE,
                "courseid": course_map.moodle_course_id,
                "component": course_map.grade_component,
                "activityid": course_map.grade_activity_id,
                "itemnumber": course_map.grade_item_number,
                "grades[0][studentid]": user_map.moodle_user_id,
                "grades[0][grade]": grade_record.numeric_score,
            },
        )

    def _resolve_enrollment(self, payload: dict[str, Any]) -> Enrollment:
        enrollment_id = payload.get("enrollment_id")
        if enrollment_id:
            return Enrollment.objects.select_related("student__user", "section__course", "section__faculty_user").get(
                pk=enrollment_id
            )
        student_id = payload.get("student_id")
        section_id = payload.get("section_id")
        if not student_id or not section_id:
            raise MoodleSyncError("Enrollment sync payload is missing identifiers.")
        return (
            Enrollment.objects.select_related("student__user", "section__course", "section__faculty_user")
            .filter(student_id=student_id, section_id=section_id)
            .order_by("-updated_at", "-enrolled_at")
            .first()
        ) or self._raise_missing_enrollment()

    def _request(self, wsfunction: str, payload: dict[str, Any]) -> Any:
        self._require_config()
        request_payload = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
            **payload,
        }
        try:
            response = requests.post(self.endpoint, data=request_payload, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise MoodleSyncError(f"Moodle REST request failed for {wsfunction}.") from exc

        try:
            response_payload = response.json()
        except ValueError as exc:
            raise MoodleSyncError(f"Moodle REST returned invalid JSON for {wsfunction}.") from exc

        if isinstance(response_payload, dict) and "exception" in response_payload:
            exception_name = response_payload.get("exception", "unknown_exception")
            error_code = response_payload.get("errorcode", "unknown_error")
            message = response_payload.get("message", "No Moodle error message was provided.")
            raise MoodleSyncError(f"Moodle REST returned {exception_name} ({error_code}) for {wsfunction}: {message}")

        return response_payload

    def _require_config(self):
        if not self.base_url:
            raise MoodleSyncError("MOODLE_BASE_URL is not configured.")
        if not self.token:
            raise MoodleSyncError("MOODLE_WS_TOKEN is not configured.")

    def _build_course_shortname(self, section: CourseSection) -> str:
        academic_year = section.academic_year.replace("/", "_").replace(" ", "")
        semester = section.semester.replace("Semester", "SEM").replace(" ", "")
        return f"{section.course.course_code}-{section.section_code}-{academic_year}-{semester}"

    def _build_course_fullname(self, section: CourseSection) -> str:
        return f"{section.course.course_title} - {section.section_code} ({section.semester} {section.academic_year})"

    def _build_course_summary(self, section: CourseSection) -> str:
        return (
            f"{section.course.course_code} {section.course.course_title}. "
            f"Section {section.section_code}, {section.semester} {section.academic_year}."
        )

    def _user_name_parts(self, user: User) -> MoodleUserNameParts:
        if user.first_name or user.last_name:
            firstname = (user.first_name or user.username).strip()
            lastname = (user.last_name or user.username).strip()
            return MoodleUserNameParts(firstname=firstname, lastname=lastname)
        if user.full_name.strip():
            pieces = [piece for piece in user.full_name.strip().split() if piece]
            if len(pieces) == 1:
                return MoodleUserNameParts(firstname=pieces[0], lastname=user.username)
            return MoodleUserNameParts(firstname=pieces[0], lastname=" ".join(pieces[1:]))
        return MoodleUserNameParts(firstname=user.username, lastname=user.username)

    def _generate_temporary_password(self) -> str:
        return f"Sis!{secrets.token_urlsafe(12)}9"

    def _looks_like_existing_user_error(self, exc: MoodleSyncError) -> bool:
        message = str(exc).lower()
        return "username already exists" in message or "email address already exists" in message

    def _raise_missing_enrollment(self):
        raise MoodleSyncError("The enrollment sync payload did not resolve to an enrollment record.")
