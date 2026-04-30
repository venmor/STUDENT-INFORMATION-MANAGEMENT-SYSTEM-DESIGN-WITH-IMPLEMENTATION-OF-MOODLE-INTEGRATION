import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_full_name_user_must_reset_password_accesslog"),
        ("academics", "0002_seed_defaults"),
        ("students", "0002_studentcorrectionrequest"),
        ("integration", "0003_ltioidcstate_ltilaunchsession"),
    ]

    operations = [
        migrations.CreateModel(
            name="MoodleEngagementIngestionRun",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("RUNNING", "Running"),
                            ("SUCCEEDED", "Succeeded"),
                            ("PARTIAL", "Partial"),
                            ("FAILED", "Failed"),
                            ("DRY_RUN", "Dry run"),
                        ],
                        default="RUNNING",
                        max_length=16,
                    ),
                ),
                ("dry_run", models.BooleanField(default=False)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("courses_inspected", models.PositiveIntegerField(default=0)),
                ("users_inspected", models.PositiveIntegerField(default=0)),
                ("snapshots_created", models.PositiveIntegerField(default=0)),
                ("snapshots_updated", models.PositiveIntegerField(default=0)),
                ("skipped_unmapped_users", models.PositiveIntegerField(default=0)),
                ("failure_count", models.PositiveIntegerField(default=0)),
                ("last_error", models.TextField(blank=True)),
                ("summary_payload", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-started_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="MoodleEngagementSnapshot",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("moodle_user_id", models.PositiveIntegerField()),
                ("moodle_course_id", models.PositiveIntegerField()),
                ("moodle_last_access_at", models.DateTimeField(blank=True, null=True)),
                ("moodle_course_last_access_at", models.DateTimeField(blank=True, null=True)),
                ("assignment_submission_count", models.PositiveIntegerField(blank=True, null=True)),
                ("assignment_submission_rate", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("quiz_attempt_count", models.PositiveIntegerField(blank=True, null=True)),
                ("quiz_average", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("forum_post_count", models.PositiveIntegerField(blank=True, null=True)),
                ("raw_summary", models.JSONField(blank=True, default=dict)),
                ("collected_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snapshots",
                        to="integration.moodleengagementingestionrun",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="moodle_engagement_snapshots",
                        to="academics.coursesection",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="moodle_engagement_snapshots",
                        to="students.studentprofile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="moodle_engagement_snapshots",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "ordering": ["-collected_at", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="moodleengagementsnapshot",
            index=models.Index(fields=["moodle_user_id", "moodle_course_id"], name="integration_moodle__79a056_idx"),
        ),
        migrations.AddIndex(
            model_name="moodleengagementsnapshot",
            index=models.Index(fields=["section", "collected_at"], name="integration_section_d80fde_idx"),
        ),
        migrations.AddIndex(
            model_name="moodleengagementsnapshot",
            index=models.Index(fields=["student", "collected_at"], name="integration_student_9b898e_idx"),
        ),
        migrations.AddConstraint(
            model_name="moodleengagementsnapshot",
            constraint=models.UniqueConstraint(
                fields=("run", "moodle_user_id", "moodle_course_id"),
                name="unique_moodle_engagement_snapshot_per_run_user_course",
            ),
        ),
    ]
