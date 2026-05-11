from __future__ import annotations

from rest_framework import serializers

from .models import AnalyticsETLRun, StudentAnalyticsSnapshot


class AnalyticsETLRunSerializer(serializers.ModelSerializer):
    startedAt = serializers.DateTimeField(source="started_at")
    completedAt = serializers.DateTimeField(source="completed_at", allow_null=True)
    studentsProcessed = serializers.IntegerField(source="students_processed")
    snapshotsCreated = serializers.IntegerField(source="snapshots_created")
    snapshotsUpdated = serializers.IntegerField(source="snapshots_updated")
    moodleSnapshotsUsed = serializers.IntegerField(source="moodle_snapshots_used")
    failureCount = serializers.IntegerField(source="failure_count")
    lastError = serializers.CharField(source="last_error")
    dryRun = serializers.BooleanField(source="dry_run")

    class Meta:
        model = AnalyticsETLRun
        fields = (
            "id",
            "status",
            "startedAt",
            "completedAt",
            "studentsProcessed",
            "snapshotsCreated",
            "snapshotsUpdated",
            "moodleSnapshotsUsed",
            "failureCount",
            "lastError",
            "dryRun",
            "metadata",
        )


class StudentAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    academicYear = serializers.CharField(source="academic_year")
    yearOfStudy = serializers.IntegerField(source="year_of_study")
    academicStanding = serializers.CharField(source="academic_standing")
    attendanceAverage = serializers.DecimalField(source="attendance_average", max_digits=5, decimal_places=2, allow_null=True)
    financialFlagCount = serializers.IntegerField(source="financial_flag_count")
    activeEnrollmentCount = serializers.IntegerField(source="active_enrollment_count")
    draftGradeCount = serializers.IntegerField(source="draft_grade_count")
    officialGradeCount = serializers.IntegerField(source="official_grade_count")
    latestMoodleAccessAt = serializers.DateTimeField(source="latest_moodle_access_at", allow_null=True)
    latestMoodleCourseAccessAt = serializers.DateTimeField(source="latest_moodle_course_access_at", allow_null=True)
    moodleSnapshotCount = serializers.IntegerField(source="moodle_snapshot_count")
    sourceRunId = serializers.UUIDField(source="source_run_id")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = StudentAnalyticsSnapshot
        fields = (
            "id",
            "student",
            "academicYear",
            "semester",
            "programme",
            "yearOfStudy",
            "academicStanding",
            "attendanceAverage",
            "financialFlagCount",
            "activeEnrollmentCount",
            "draftGradeCount",
            "officialGradeCount",
            "gpa",
            "latestMoodleAccessAt",
            "latestMoodleCourseAccessAt",
            "moodleSnapshotCount",
            "sourceRunId",
            "metadata",
            "createdAt",
            "updatedAt",
        )

    def get_student(self, obj: StudentAnalyticsSnapshot):
        return {
            "id": str(obj.student_id),
            "studentNumber": obj.student.student_number,
            "fullName": obj.student.user.full_name or obj.student.user.username,
            "programme": obj.student.programme,
        }


class AnalyticsSummarySerializer(serializers.Serializer):
    latestRun = AnalyticsETLRunSerializer(allow_null=True)
    studentsWithSnapshots = serializers.IntegerField()
    moodleSnapshotsUsed = serializers.IntegerField()
    averageAttendance = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    officialGradeCount = serializers.IntegerField()
    financialFlags = serializers.IntegerField()
    latestMoodleAccessAt = serializers.DateTimeField(allow_null=True)
