from django.conf import settings
from django.core.management.base import BaseCommand

from apps.accounts.constants import RoleCode
from apps.accounts.models import Role, User
from apps.students.models import StudentProfile
from apps.summarisation.models import SummarisationRequest
from apps.summarisation.services import approve_summarisation, create_summarisation_request


DEMO_SCENARIOS = [
    {
        "title": "Academic probation meeting",
        "raw_text": (
            "Met with student regarding poor performance this semester. "
            "Currently on academic probation after failing two core courses last term. "
            "Student reports difficulty concentrating due to part-time job taking too many hours. "
            "Discussed reducing work hours and using campus tutoring services. "
            "Student agreed to attend at least two tutoring sessions per week and will "
            "submit a revised study schedule by next Friday."
        ),
        "approve": True,
        "edited_output": {
            "key_issues": [
                "Academic probation after failing two core courses",
                "Part-time job hours interfering with study time",
                "Difficulty concentrating reported by student",
            ],
            "recommended_actions": [
                "Reduce work hours to maximum 10 per week",
                "Attend campus tutoring at least twice weekly",
                "Submit revised study schedule by next Friday",
            ],
            "urgency_level": "Follow-up Needed",
        },
    },
    {
        "title": "Course withdrawal discussion",
        "raw_text": (
            "Student requesting to withdraw from MATH201 past the official deadline. "
            "Reason: family emergency requiring travel for three weeks during mid-semester. "
            "Student has documentation from hospital confirming family member illness. "
            "Financial aid office confirmed no impact on scholarship if approved as extenuating circumstances. "
            "Recommended filing the late withdrawal form with supporting documents by end of this week."
        ),
        "approve": True,
        "edited_output": {
            "key_issues": [
                "Late withdrawal request for MATH201 past deadline",
                "Family emergency with hospital documentation",
                "Financial aid confirmed no scholarship impact",
            ],
            "recommended_actions": [
                "File late withdrawal form with supporting documents",
                "Submit by end of this week",
                "Follow up with financial aid office for confirmation letter",
            ],
            "urgency_level": "Urgent",
        },
    },
    {
        "title": "Graduate school preparation",
        "raw_text": (
            "Third-year student interested in applying to MSc programmes in data science. "
            "GPA currently 3.4, needs to maintain above 3.2 for target programmes. "
            "Discussed research opportunities with Dr. Smith in the ML lab. "
            "Student needs two recommendation letters, currently has one confirmed. "
            "Advised to join the undergraduate research programme next semester and "
            "start drafting personal statement over the summer break."
        ),
        "approve": False,
        "edited_output": None,
    },
    {
        "title": "Personal circumstances extension",
        "raw_text": (
            "Student requesting two-week extension on all assignments due to death in immediate family. "
            "Student has been absent for one week already. Bereavement policy allows up to "
            "two weeks of compassionate leave with documentation. Student provided death certificate. "
            "Contacted all three course lecturers who confirmed extensions are acceptable. "
            "Student will return to campus next Monday and submit revised completion dates."
        ),
        "approve": True,
        "edited_output": {
            "key_issues": [
                "Bereavement leave request following death in immediate family",
                "One week absence already taken",
                "All course lecturers confirmed extension acceptable",
            ],
            "recommended_actions": [
                "Approve two-week compassionate leave per bereavement policy",
                "Record documentation on file",
                "Student to submit revised completion dates upon return Monday",
            ],
            "urgency_level": "Urgent",
        },
    },
    {
        "title": "Internship credit approval",
        "raw_text": (
            "Student seeking academic credit for summer internship at TechCorp Ltd. "
            "Role is software development, 12 weeks full-time. Supervisor confirmed "
            "willingness to complete evaluation form. Checked programme requirements: "
            "internship credit available under COSC490 if minimum 300 hours and relevant to degree. "
            "Student needs to submit placement agreement form and learning objectives "
            "before internship start date of June 1."
        ),
        "approve": False,
        "edited_output": None,
    },
]


class Command(BaseCommand):
    help = "Seed demonstration summarisation requests with real-world advising scenarios."

    def handle(self, *args, **options):
        Role.objects.get_or_create(code=RoleCode.ADVISOR, defaults={"name": "Advisor"})
        Role.objects.get_or_create(code=RoleCode.STUDENT, defaults={"name": "Student"})

        advisor, _ = User.objects.get_or_create(
            username="advisor.demo1",
            defaults={"primary_role": RoleCode.ADVISOR, "full_name": "Demo Advisor"},
        )
        if not advisor.has_usable_password():
            advisor.set_password("DemoPass123!")
            advisor.save()

        student_user, _ = User.objects.get_or_create(
            username="student.demo1",
            defaults={"primary_role": RoleCode.STUDENT, "full_name": "Demo Student"},
        )
        if not student_user.has_usable_password():
            student_user.set_password("DemoPass123!")
            student_user.save()

        student, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                "student_number": "STU001",
                "date_of_birth": "2001-05-15",
                "gender": "M",
                "programme": "BSc Computer Science",
                "year_of_study": 3,
            },
        )

        created_count = 0
        approved_count = 0

        original_provider = settings.AI_PROVIDER

        for scenario in DEMO_SCENARIOS:
            existing = SummarisationRequest.objects.filter(
                user=advisor, raw_input_text__startswith=scenario["raw_text"][:80]
            ).first()
            if existing:
                self.stdout.write(f"  Skipping existing: {scenario['title']}")
                continue

            settings.AI_PROVIDER = "deterministic"

            summarisation = create_summarisation_request(
                user=advisor,
                raw_text=scenario["raw_text"],
                student=student,
            )
            created_count += 1
            self.stdout.write(f"  Created: {scenario['title']}")

            if scenario["approve"] and scenario["edited_output"]:
                approve_summarisation(
                    user=advisor,
                    summarisation=summarisation,
                    human_edited_output=scenario["edited_output"],
                )
                approved_count += 1
                self.stdout.write(f"  Approved: {scenario['title']}")

        settings.AI_PROVIDER = original_provider

        self.stdout.write(self.style.SUCCESS(
            f"Summarisation demo seeded: {created_count} created, {approved_count} approved."
        ))
