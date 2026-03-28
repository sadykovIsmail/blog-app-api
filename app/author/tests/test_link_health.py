from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from author.models import AuthorModel, BlogPostModel, Citation

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


class LinkHealthCommandTests(TestCase):
    def setUp(self):
        self.user = create_user("lhuser")
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.citation = Citation.objects.create(
            post=self.post, url="https://example.com",
        )

    @patch("author.management.commands.check_link_health.requests.head")
    def test_command_updates_http_status(self, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://example.com"
        mock_head.return_value = mock_resp

        call_command("check_link_health")

        self.citation.refresh_from_db()
        self.assertEqual(self.citation.http_status, 200)

    @patch("author.management.commands.check_link_health.requests.head")
    def test_command_updates_checked_at(self, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://example.com"
        mock_head.return_value = mock_resp

        call_command("check_link_health")

        self.citation.refresh_from_db()
        self.assertIsNotNone(self.citation.checked_at)

    @patch("author.management.commands.check_link_health.requests.head")
    def test_command_stores_canonical_url(self, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 301
        mock_resp.url = "https://example.com/canonical"
        mock_head.return_value = mock_resp

        call_command("check_link_health")

        self.citation.refresh_from_db()
        self.assertEqual(self.citation.canonical_url, "https://example.com/canonical")

    @patch("author.management.commands.check_link_health.requests.head")
    def test_command_handles_connection_error(self, mock_head):
        import requests
        mock_head.side_effect = requests.RequestException("connection failed")

        call_command("check_link_health")

        self.citation.refresh_from_db()
        self.assertEqual(self.citation.http_status, 0)
        self.assertIsNotNone(self.citation.checked_at)
