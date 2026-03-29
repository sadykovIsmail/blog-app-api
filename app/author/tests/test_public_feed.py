from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()
PUBLIC_FEED_URL = reverse("public-post-list")


def create_user(username, password="pass123"):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@test.com")


def create_post(user, author, title="Post", content="body",
                post_status="PUBLISHED", visibility="PUBLIC"):
    return BlogPostModel.objects.create(
        user=user, author=author, title=title, content=content,
        status=post_status, visibility=visibility,
    )


class PublicFeedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("feeduser")
        self.author = create_author(self.user)

    def test_unauthenticated_can_access_public_feed(self):
        res = self.client.get(PUBLIC_FEED_URL)
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_published_public_posts_returned(self):
        create_post(self.user, self.author, title="Published Public",
                    post_status="PUBLISHED", visibility="PUBLIC")
        create_post(self.user, self.author, title="Draft Post",
                    post_status="DRAFT", visibility="PUBLIC")
        create_post(self.user, self.author, title="Unlisted Published",
                    post_status="PUBLISHED", visibility="UNLISTED")
        create_post(self.user, self.author, title="Archived Post",
                    post_status="ARCHIVED", visibility="PUBLIC")

        res = self.client.get(PUBLIC_FEED_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in res.data["results"]]
        self.assertIn("Published Public", titles)
        self.assertNotIn("Draft Post", titles)
        self.assertNotIn("Unlisted Published", titles)
        self.assertNotIn("Archived Post", titles)

    def test_feed_is_paginated(self):
        for i in range(15):
            create_post(self.user, self.author, title=f"Post {i}")
        res = self.client.get(PUBLIC_FEED_URL)
        self.assertIn("results", res.data)
        self.assertIn("count", res.data)
        self.assertIn("next", res.data)

    def test_feed_returns_expected_fields(self):
        create_post(self.user, self.author, title="Field Check")
        res = self.client.get(PUBLIC_FEED_URL)
        post = res.data["results"][0]
        for field in ["id", "title", "slug", "status", "visibility", "published_at"]:
            self.assertIn(field, post)
