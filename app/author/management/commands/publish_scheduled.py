from django.core.management.base import BaseCommand
from django.utils import timezone
from author.models import BlogPostModel


class Command(BaseCommand):
    help = "Publish posts whose scheduled_for datetime has passed."

    def handle(self, *args, **options):
        now = timezone.now()
        qs = BlogPostModel.objects.filter(
            status=BlogPostModel.Status.SCHEDULED,
            scheduled_for__lte=now,
        )
        count = qs.count()
        qs.update(status=BlogPostModel.Status.PUBLISHED, published_at=now)
        self.stdout.write(self.style.SUCCESS(f"Published {count} scheduled post(s)."))
