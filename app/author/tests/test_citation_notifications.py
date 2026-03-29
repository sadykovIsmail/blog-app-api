from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from author.models import AuthorModel, BlogPostModel, Citation, Notification

User = get_user_model()


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def create_post(user, author):
    return BlogPostModel.objects.create(
        user=user, author=author, title="Post", content="body",
        status="PUBLISHED", visibility="PUBLIC",
    )


class CitationNotificationTests(TestCase):
    def setUp(self):
        self.user = create_user("cnuser")
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)

    @patch("author.management.commands.check_link_health.requests.head")
    def test_dead_link_creates_notification(self, mock_head):
        citation = Citation.objects.create(
            post=self.post, url="https://dead.example.com",
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.url = "https://dead.example.com"
        mock_resp.headers = {}
        mock_head.return_value = mock_resp

        call_command("check_link_health")

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.post.user,
                notification_type="citation_dead",
            ).exists()
        )

    @patch("author.management.commands.check_link_health.requests.head")
    def test_content_drift_creates_notification(self, mock_head):
        citation = Citation.objects.create(
            post=self.post,
            url="https://drifted.example.com",
            content_hash="oldhash",
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://drifted.example.com"
        mock_resp.headers = {"ETag": "newhash"}
        mock_head.return_value = mock_resp

        call_command("check_link_health")

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.post.user,
                notification_type="citation_drift",
            ).exists()
        )

    @patch("author.management.commands.check_link_health.requests.head")
    def test_healthy_link_creates_no_notification(self, mock_head):
        import hashlib
        content = "stablehash"
        existing_hash = hashlib.sha256(content.encode()).hexdigest()
        Citation.objects.create(
            post=self.post,
            url="https://healthy.example.com",
            content_hash=existing_hash,
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://healthy.example.com"
        mock_resp.headers = {"ETag": content}
        mock_head.return_value = mock_resp

        call_command("check_link_health")

        self.assertFalse(Notification.objects.filter(recipient=self.post.user).exists())
