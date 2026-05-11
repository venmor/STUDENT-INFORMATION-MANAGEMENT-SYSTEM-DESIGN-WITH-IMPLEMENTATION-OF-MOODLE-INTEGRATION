from django.core.management.base import BaseCommand
from django.db import transaction

from apps.structure.models import Department, Programme, School, Stream


class Command(BaseCommand):
    help = "Seed the academic structure hierarchy with demo data"

    @transaction.atomic
    def handle(self, *args, **options):
        school_sonhas, _ = School.objects.get_or_create(
            code="SoNHAS",
            defaults={"name": "School of Natural and Health Applied Sciences"},
        )
        school_sobe, _ = School.objects.get_or_create(
            code="SoBE",
            defaults={"name": "School of Business and Economics"},
        )
        school_soeduc, _ = School.objects.get_or_create(
            code="SoEduc",
            defaults={"name": "School of Education"},
        )

        dept_cs, _ = Department.objects.get_or_create(
            code="CS",
            defaults={"name": "Department of Computer Science", "school": school_sonhas},
        )
        dept_math, _ = Department.objects.get_or_create(
            code="MATH",
            defaults={"name": "Department of Mathematics", "school": school_sonhas},
        )
        dept_acct, _ = Department.objects.get_or_create(
            code="ACCT",
            defaults={"name": "Department of Accounting", "school": school_sobe},
        )
        dept_educ, _ = Department.objects.get_or_create(
            code="EDUC",
            defaults={"name": "Department of Education", "school": school_soeduc},
        )

        prog_bsc_cs, _ = Programme.objects.get_or_create(
            code="BSc-CS",
            defaults={
                "name": "Bachelor of Science in Computer Science",
                "department": dept_cs,
                "level": "UG",
                "duration_years": 4,
            },
        )
        prog_bsc_math, _ = Programme.objects.get_or_create(
            code="BSc-MATH",
            defaults={
                "name": "Bachelor of Science in Mathematics",
                "department": dept_math,
                "level": "UG",
                "duration_years": 4,
            },
        )
        prog_bba, _ = Programme.objects.get_or_create(
            code="BBA",
            defaults={
                "name": "Bachelor of Business Administration",
                "department": dept_acct,
                "level": "UG",
                "duration_years": 4,
            },
        )
        prog_msc_cs, _ = Programme.objects.get_or_create(
            code="MSc-CS",
            defaults={
                "name": "Master of Science in Computer Science",
                "department": dept_cs,
                "level": "PG",
                "duration_years": 2,
            },
        )

        Stream.objects.get_or_create(
            code="CS-SE",
            defaults={"name": "Software Engineering", "programme": prog_bsc_cs},
        )
        Stream.objects.get_or_create(
            code="CS-NET",
            defaults={"name": "Networking and Cyber Security", "programme": prog_bsc_cs},
        )
        Stream.objects.get_or_create(
            code="CS-DS",
            defaults={"name": "Data Science", "programme": prog_bsc_cs},
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {School.objects.count()} schools, "
            f"{Department.objects.count()} departments, "
            f"{Programme.objects.count()} programmes, "
            f"{Stream.objects.count()} streams"
        ))
