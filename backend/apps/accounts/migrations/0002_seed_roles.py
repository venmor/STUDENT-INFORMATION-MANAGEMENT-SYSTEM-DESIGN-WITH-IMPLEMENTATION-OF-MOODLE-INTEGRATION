from django.db import migrations


ROLE_ROWS = [
    {
        "code": "STUDENT",
        "name": "Student",
        "description": "Student-facing academic and registration access.",
        "is_staff_role": False,
    },
    {
        "code": "ADVISOR",
        "name": "Advisor",
        "description": "Academic advising and student support access.",
        "is_staff_role": True,
    },
    {
        "code": "FACULTY",
        "name": "Faculty",
        "description": "Teaching, roster, and grade-entry access.",
        "is_staff_role": True,
    },
    {
        "code": "ADMIN",
        "name": "Admin",
        "description": "Administrative and platform management access.",
        "is_staff_role": True,
    },
]


def seed_roles(apps, schema_editor):
    role_model = apps.get_model("accounts", "Role")
    for row in ROLE_ROWS:
        role_model.objects.update_or_create(code=row["code"], defaults=row)


def unseed_roles(apps, schema_editor):
    role_model = apps.get_model("accounts", "Role")
    role_model.objects.filter(code__in=[row["code"] for row in ROLE_ROWS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, reverse_code=unseed_roles),
    ]
