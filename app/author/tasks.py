"""
Celery async tasks for the author app.

These tasks are registered with Celery and can be:
  - Triggered on-demand:  task.delay() / task.apply_async()
  - Scheduled via Celery Beat (see CELERY_BEAT_SCHEDULE in settings.py)
"""
import hashlib
import logging

import requests
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_link_health_task(self):
    """
    Check the HTTP status of every citation URL and notify post authors
    about dead links (4xx / 5xx / connection errors) or content drift.

    Runs daily at 02:00 UTC via Celery Beat.
    """
    from author.models import Citation, Notification

    citations = Citation.objects.select_related('post__user').all()
    checked = dead = drifted = 0

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
            content = (
                response.headers.get("ETag", "")
                + response.headers.get("Last-Modified", "")
            )
            new_hash = hashlib.sha256(content.encode()).hexdigest() if content else ""
        except requests.RequestException as exc:
            logger.warning("Citation check failed for %s: %s", citation.url, exc)
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
            dead += 1
        elif old_hash and new_hash and old_hash != new_hash:
            Notification.objects.create(
                recipient=post_owner,
                notification_type="citation_drift",
                post=citation.post,
            )
            drifted += 1

        checked += 1

    logger.info("check_link_health_task: checked=%d dead=%d drifted=%d", checked, dead, drifted)
    return {"checked": checked, "dead": dead, "drifted": drifted}


@shared_task
def publish_scheduled_task():
    """
    Publish blog posts whose scheduled_for datetime has passed.

    Runs every 5 minutes via Celery Beat.
    """
    from author.models import BlogPostModel

    now = timezone.now()
    qs = BlogPostModel.objects.filter(
        status=BlogPostModel.Status.SCHEDULED,
        scheduled_for__lte=now,
    )
    count = qs.count()
    qs.update(status=BlogPostModel.Status.PUBLISHED, published_at=now)
    logger.info("publish_scheduled_task: published %d post(s)", count)
    return {"published": count}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email_task(self, user_id: int):
    """
    Send a welcome e-mail to a newly registered user.

    Triggered on registration (call via .delay(user.id)).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("send_welcome_email_task: user %d not found", user_id)
        return

    try:
        send_mail(
            subject="Welcome to the Blog Platform!",
            message=(
                f"Hi {user.username},\n\n"
                "Thanks for joining! Start writing your first post today.\n\n"
                "— The Blog Team"
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@blogplatform.com"),
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("send_welcome_email_task: sent welcome email to user %d", user_id)
    except Exception as exc:
        logger.error("send_welcome_email_task: failed for user %d — %s", user_id, exc)
        raise self.retry(exc=exc)
