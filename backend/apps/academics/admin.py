from django.contrib import admin

from .models import (
    AcademicStandingRule,
    AttendanceRecord,
    AttendanceSession,
    Course,
    CoursePrerequisite,
    CourseSection,
    Enrollment,
    EnrollmentEvent,
    GradeChangeLog,
    GradeRecord,
    GradingScaleBand,
    SectionTimetable,
    WaitlistEntry,
)


admin.site.register(Course)
admin.site.register(CoursePrerequisite)
admin.site.register(CourseSection)
admin.site.register(SectionTimetable)
admin.site.register(Enrollment)
admin.site.register(EnrollmentEvent)
admin.site.register(WaitlistEntry)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
admin.site.register(GradingScaleBand)
admin.site.register(AcademicStandingRule)
admin.site.register(GradeRecord)
admin.site.register(GradeChangeLog)
