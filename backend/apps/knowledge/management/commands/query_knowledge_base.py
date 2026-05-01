from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.knowledge.services import test_knowledge_retrieval


class Command(BaseCommand):
    help = "Run a retrieval-only test query against the configured knowledge vector store."

    def add_arguments(self, parser):
        parser.add_argument("query", help="Question to embed and retrieve against the institutional knowledge base.")
        parser.add_argument("--limit", type=int, default=5)
        parser.add_argument("--source-type", default="")

    def handle(self, *args, **options):
        results = test_knowledge_retrieval(
            options["query"],
            limit=options["limit"],
            source_type=options.get("source_type") or "",
        )
        if not results:
            raise CommandError("No relevant chunks were retrieved.")
        self.stdout.write(self.style.SUCCESS("Knowledge retrieval test complete"))
        self.stdout.write("No LLM answer was generated.")
        for index, result in enumerate(results, start=1):
            preview = result["text"][:220].replace("\n", " ")
            self.stdout.write(f"{index}. {result['sourceTitle']} ({result['sourceType']})")
            self.stdout.write(f"   score: {result['score']}")
            self.stdout.write(f"   chunk id: {result['chunkId']}")
            self.stdout.write(f"   preview: {preview}")
