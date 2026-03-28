from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()
POSTS_URL = reverse("blogpostmodel-list")


def create_user(username, password="pass123"):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@test.com")


class PostSlugDatesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("sluguser")
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_slug_auto_generated_from_title(self):
        payload = {"title": "My Awesome Post", "content": "x", "author": self.author.id}
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["slug"], "my-awesome-post")

    def test_slug_is_unique_with_suffix(self):
        payload = {"title": "Same Title", "content": "x", "author": self.author.id}
        res1 = self.client.post(POSTS_URL, payload)
        res2 = self.client.post(POSTS_URL, payload)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(res1.data["slug"], res2.data["slug"])

    def test_published_at_set_when_status_published(self):
        payload = {
            "title": "Go Live", "content": "x",
            "author": self.author.id, "status": "PUBLISHED",
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data["published_at"])

    def test_published_at_null_when_draft(self):
        payload = {"title": "Still Draft", "content": "x", "author": self.author.id}
        res = self.client.post(POSTS_URL, payload)
        self.assertIsNone(res.data["published_at"])

    def test_scheduled_for_can_be_set(self):
        future = (timezone.now() + timezone.timedelta(days=1)).isoformat()
        payload = {
            "title": "Future Post", "content": "x",
            "author": self.author.id,
            "status": "SCHEDULED", "scheduled_for": future,
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data["scheduled_for"])

    def test_slug_in_list_response(self):
        BlogPostModel.objects.create(
            user=self.user, author=self.author,
            title="Has Slug", content="x",
        )
        res = self.client.get(POSTS_URL)
        self.assertIn("slug", res.data[0])
