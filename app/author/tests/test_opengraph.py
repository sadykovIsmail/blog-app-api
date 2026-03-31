from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


def make_post(user, title="OG Post"):
    author = AuthorModel.objects.create(name="A", email="a@a.com", user=user)
    return BlogPostModel.objects.create(
        title=title, content="This is the post content for OG testing.",
        author=author, user=user, status="PUBLISHED", visibility="PUBLIC",
        published_at=timezone.now(),
    )


class OpenGraphTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("oguser")
        self.post = make_post(self.user)

    def test_og_endpoint_returns_200(self):
        res = self.client.get(f"/api/public/posts/{self.post.slug}/og/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_og_contains_title(self):
        res = self.client.get(f"/api/public/posts/{self.post.slug}/og/")
        self.assertEqual(res.data["og_title"], self.post.title)

    def test_og_contains_description(self):
        res = self.client.get(f"/api/public/posts/{self.post.slug}/og/")
        self.assertIn("og_description", res.data)
        self.assertTrue(len(res.data["og_description"]) > 0)

    def test_og_contains_url(self):
        res = self.client.get(f"/api/public/posts/{self.post.slug}/og/")
        self.assertIn("og_url", res.data)
        self.assertIn(self.post.slug, res.data["og_url"])

    def test_og_contains_author(self):
        res = self.client.get(f"/api/public/posts/{self.post.slug}/og/")
        self.assertEqual(res.data["og_author"], self.user.handle)

    def test_og_no_auth_required(self):
        res = self.client.get(f"/api/public/posts/{self.post.slug}/og/")
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_og_nonexistent_slug_returns_404(self):
        res = self.client.get("/api/public/posts/does-not-exist/og/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
