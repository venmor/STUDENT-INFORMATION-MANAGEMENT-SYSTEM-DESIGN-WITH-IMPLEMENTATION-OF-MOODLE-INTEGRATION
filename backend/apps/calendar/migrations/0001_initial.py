from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("academics", "0002_seed_defaults"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademicCalendarEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("REGISTRATION_OPEN", "Registration Open"),
                            ("REGISTRATION_DEADLINE", "Registration Deadline"),
                            ("DROP_DEADLINE", "Drop Deadline"),
                            ("EXAM_PERIOD", "Exam Period"),
                            ("GRADE_SUBMISSION_DEADLINE", "Grade Submission Deadline"),
                            ("TERM_START", "Term Start"),
                            ("TERM_END", "Term End"),
                            ("MOODLE_ACTIVITY", "Moodle Activity"),
                            ("ADVISING", "Advising"),
                            ("GENERAL", "General"),
                        ],
                        max_length=40,
                    ),
                ),
                (
                    "audience",
                    models.CharField(
                        choices=[
                            ("ALL", "All"),
                            ("STUDENTS", "Students"),
                            ("FACULTY", "Faculty"),
                            ("ADVISORS", "Advisors"),
                            ("ADMINS", "Admins"),
                        ],
                        default="ALL",
                        max_length=16,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("LOW", "Low"),
                            ("NORMAL", "Normal"),
                            ("HIGH", "High"),
                            ("CRITICAL", "Critical"),
                        ],
                        default="NORMAL",
                        max_length=16,
                    ),
                ),
                ("academic_year", models.CharField(max_length=32)),
                ("semester", models.CharField(max_length=64)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField(blank=True, null=True)),
                ("all_day", models.BooleanField(default=False)),
                ("location", models.CharField(blank=True, max_length=160)),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("MANUAL", "Manual"),
                            ("COURSE_SECTION", "Course Section"),
                            ("SYSTEM", "System"),
                            ("MOODLE", "Moodle"),
                        ],
                        default="MANUAL",
                        max_length=24,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("CANCELLED", "Cancelled"),
                            ("DRAFT", "Draft"),
                        ],
                        default="ACTIVE",
                        max_length=16,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_academic_calendar_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "related_course_section",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="academic_calendar_events",
                        to="academics.coursesection",
                    ),
                ),
            ],
            options={
                "ordering": ["start_at", "title", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="academiccalendarevent",
            index=models.Index(fields=["start_at"], name="calendar_start_idx"),
        ),
        migrations.AddIndex(
            model_name="academiccalendarevent",
            index=models.Index(fields=["event_type", "start_at"], name="calendar_type_start_idx"),
        ),
        migrations.AddIndex(
            model_name="academiccalendarevent",
            index=models.Index(fields=["audience", "status", "start_at"], name="calendar_aud_stat_start_idx"),
        ),
        migrations.AddIndex(
            model_name="academiccalendarevent",
            index=models.Index(fields=["academic_year", "semester"], name="calendar_year_sem_idx"),
        ),
        migrations.AddIndex(
            model_name="academiccalendarevent",
            index=models.Index(fields=["source", "related_course_section", "event_type"], name="calendar_source_section_idx"),
        ),
        migrations.AddConstraint(
            model_name="academiccalendarevent",
            constraint=models.UniqueConstraint(fields=("source", "related_course_section", "event_type"), name="calendar_unique_source_section_type"),
        ),
    ]
