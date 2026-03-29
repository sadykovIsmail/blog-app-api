import hashlib
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from author.models import Citation, Notification


class Command(BaseCommand):
    help = "Check the health of all citation URLs and update their status fields."

    def handle(self, *args, **options):
        citations = Citation.objects.select_related('post__user').all()
        updated = 0

        for citation in citations:
            old_hash = citation.content_hash
            try:
                response = requests.head(
                    citation.url,
                    allow_redirects=True,
                    timeout=10,
                    headers={"User-Agent": "blog-citation-checker/1.0"},
                )
                new_status = response.status_code
                citation.canonical_url = response.url or ""
                content = response.headers.get("ETag", "") + response.headers.get("Last-Modified", "")
                new_hash = hashlib.sha256(content.encode()).hexdigest() if content else ""
            except requests.RequestException as e:
                self.stderr.write(f"Error checking {citation.url}: {e}")
                new_status = 0
                citation.canonical_url = ""
                new_hash = ""

            citation.http_status = new_status
            citation.content_hash = new_hash
            citation.checked_at = timezone.now()
            citation.save(update_fields=["http_status", "canonical_url", "content_hash", "checked_at"])

            post_owner = citation.post.user
            if new_status >= 400 or new_status == 0:
                Notification.objects.create(
                    recipient=post_owner,
                    notification_type="citation_dead",
                    post=citation.post,
                )
            elif old_hash and new_hash and old_hash != new_hash:
                Notification.objects.create(
                    recipient=post_owner,
                    notification_type="citation_drift",
                    post=citation.post,
                )

            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Checked {updated} citation(s)."))
