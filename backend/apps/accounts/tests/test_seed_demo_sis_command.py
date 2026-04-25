from io import StringIO

from django.core.management import call_command

from apps.accounts.models import User
from apps.academics.models import Course, CourseSection, Enrollment, GradeRecord
from apps.students.models import AdvisingNote, FinancialFlag, StudentCorrectionRequest, StudentProfile


def test_seed_demo_sis_command_is_repeatable(db):
    stdout = StringIO()

    call_command("seed_demo_sis", stdout=stdout)
    call_command("seed_demo_sis", stdout=stdout)

    assert User.objects.filter(username="admin.demo").count() == 1
    assert User.objects.filter(username="advisor.demo").count() == 1
    assert User.objects.filter(username="faculty.demo").count() == 1
    assert User.objects.filter(username="student.demo1").count() == 1
    assert User.objects.filter(username="student.demo2").count() == 1

    assert StudentProfile.objects.count() == 2
    assert Course.objects.count() == 3
    assert CourseSection.objects.count() == 3
    assert Enrollment.objects.filter(is_active=True).count() == 3
    assert GradeRecord.objects.count() == 3
    assert FinancialFlag.objects.count() == 1
    assert AdvisingNote.objects.count() == 2
    assert StudentCorrectionRequest.objects.count() == 1

    output = stdout.getvalue()
    assert "Demo SIS data is ready." in output
    assert "admin.demo / DemoPass123!" in output
