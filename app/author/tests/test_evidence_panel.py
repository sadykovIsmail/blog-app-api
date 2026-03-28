from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
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


class EvidencePanelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("evuser")
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        Citation.objects.create(
            post=self.post,
            url="https://example.com",
            title="Example",
            http_status=200,
        )
        Citation.objects.create(
            post=self.post,
            url="https://dead-link.com",
            title="Dead",
            http_status=404,
        )

    def _url(self, post_id):
        return reverse("post-evidence", args=[post_id])

    def test_evidence_panel_accessible_without_auth(self):
        res = self.client.get(self._url(self.post.id))
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_panel_returns_citations(self):
        res = self.client.get(self._url(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["citations"]), 2)

    def test_evidence_panel_includes_link_health_fields(self):
        res = self.client.get(self._url(self.post.id))
        citation = res.data["citations"][0]
        for field in ["url", "title", "http_status", "checked_at"]:
            self.assertIn(field, citation)

    def test_evidence_panel_unknown_post_returns_404(self):
        res = self.client.get(self._url(99999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_evidence_panel_has_post_id(self):
        res = self.client.get(self._url(self.post.id))
        self.assertEqual(res.data["post_id"], self.post.id)
