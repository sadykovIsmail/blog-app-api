import hashlib
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from author.models import Citation


class Command(BaseCommand):
    help = "Check the health of all citation URLs and update their status fields."

    def handle(self, *args, **options):
        citations = Citation.objects.all()
        updated = 0

        for citation in citations:
            try:
                response = requests.head(
                    citation.url,
                    allow_redirects=True,
                    timeout=10,
                    headers={"User-Agent": "blog-citation-checker/1.0"},
                )
                citation.http_status = response.status_code
                citation.canonical_url = response.url or ""
                content = response.headers.get("ETag", "") + response.headers.get("Last-Modified", "")
                citation.content_hash = hashlib.sha256(content.encode()).hexdigest() if content else ""
            except requests.RequestException as e:
                self.stderr.write(f"Error checking {citation.url}: {e}")
                citation.http_status = 0
                citation.canonical_url = ""
                citation.content_hash = ""

            citation.checked_at = timezone.now()
            citation.save(update_fields=["http_status", "canonical_url", "content_hash", "checked_at"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Checked {updated} citation(s)."))
