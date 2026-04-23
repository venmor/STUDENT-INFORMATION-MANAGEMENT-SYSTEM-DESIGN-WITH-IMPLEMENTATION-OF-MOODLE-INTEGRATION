# Generated manually for Modern SIS Step 2.3 default rules.

from django.db import migrations


def seed_defaults(apps, schema_editor):
    GradingScaleBand = apps.get_model("academics", "GradingScaleBand")
    AcademicStandingRule = apps.get_model("academics", "AcademicStandingRule")

    grading_scale_rows = [
        ("A", "90.00", "100.00", "4.00", True, 10),
        ("B", "80.00", "89.99", "3.00", True, 20),
        ("C", "70.00", "79.99", "2.00", True, 30),
        ("D", "60.00", "69.99", "1.00", True, 40),
        ("F", "0.00", "59.99", "0.00", False, 50),
    ]
    for letter_grade, minimum_score, maximum_score, grade_points, is_passing, display_order in grading_scale_rows:
        GradingScaleBand.objects.get_or_create(
            letter_grade=letter_grade,
            minimum_score=minimum_score,
            maximum_score=maximum_score,
            defaults={
                "grade_points": grade_points,
                "is_passing": is_passing,
                "display_order": display_order,
            },
        )

    standing_rows = [
        ("SUSPENDED", "0.00", "0.99", 10),
        ("PROBATION", "1.00", "1.99", 20),
        ("ACADEMIC_WARNING", "2.00", "2.49", 30),
        ("GOOD_STANDING", "2.50", None, 40),
    ]
    for standing, minimum_gpa, maximum_gpa, display_order in standing_rows:
        AcademicStandingRule.objects.get_or_create(
            standing=standing,
            minimum_gpa=minimum_gpa,
            maximum_gpa=maximum_gpa,
            defaults={"display_order": display_order},
        )


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, noop),
    ]
