from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User
from apps.copilot.services import answer_copilot_question


class Command(BaseCommand):
    help = "Run a deterministic student co-pilot query against seeded demo data."

    def add_arguments(self, parser):
        parser.add_argument("question", help="Question to ask the student co-pilot.")
        parser.add_argument("--username", default="student.demo1", help="Student username. Default: student.demo1")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist as exc:
            raise CommandError("Demo student does not exist. Run python manage.py seed_copilot_demo first.") from exc

        answer = answer_copilot_question(user=user, question=options["question"])
        self.stdout.write(self.style.SUCCESS("Co-pilot query complete"))
        self.stdout.write(f"Provider: {answer.assistant_message.provider}")
        self.stdout.write(f"Confidence: {answer.confidence}")
        self.stdout.write("Answer:")
        self.stdout.write(answer.answer)
        self.stdout.write("Sources:")
        if not answer.sources:
            self.stdout.write("  No source references returned.")
        for index, source in enumerate(answer.sources, start=1):
            self.stdout.write(f"  {index}. {source['title']} ({source['sourceType']})")
            self.stdout.write(f"     score: {source['score']}")
            self.stdout.write(f"     preview: {source['preview']}")
