from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()
PUBLIC_FEED_URL = reverse("public-post-list")


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def create_post(user, author, title="Post"):
    return BlogPostModel.objects.create(
        user=user, author=author, title=title, content="body",
        status="PUBLISHED", visibility="PUBLIC",
    )


class FeedPerformanceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("perfuser")
        self.author = create_author(self.user)

    def test_feed_index_on_status_and_visibility_exists(self):
        indexes = [
            idx.fields for idx in BlogPostModel._meta.indexes
        ]
        self.assertIn(['status', 'visibility'], indexes)

    def test_feed_index_on_published_at_exists(self):
        indexes = [
            idx.fields for idx in BlogPostModel._meta.indexes
        ]
        self.assertIn(['-published_at'], indexes)

    def test_feed_response_correct_after_cache(self):
        create_post(self.user, self.author, title="Cached Post")
        res = self.client.get(PUBLIC_FEED_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_cursor_pagination_returns_results(self):
        for i in range(5):
            create_post(self.user, self.author, title=f"Post {i}")
        res = self.client.get(PUBLIC_FEED_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data["results"]), 1)
