from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()
POSTS_URL = reverse("blogpostmodel-list")


def create_user(username, password="pass123"):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@example.com")


class PostStatusFieldTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("statususer")
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_post_default_status_is_draft(self):
        payload = {"title": "My Post", "content": "hello", "author": self.author.id}
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "DRAFT")

    def test_post_status_choices_are_valid(self):
        for s in ["DRAFT", "SCHEDULED", "PUBLISHED", "ARCHIVED"]:
            payload = {
                "title": f"Post {s}", "content": "x",
                "author": self.author.id, "status": s,
            }
            res = self.client.post(POSTS_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED, msg=f"Failed for status={s}")
            self.assertEqual(res.data["status"], s)

    def test_invalid_status_returns_400(self):
        payload = {"title": "Bad", "content": "x", "author": self.author.id, "status": "INVALID"}
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_update_status(self):
        post = BlogPostModel.objects.create(
            user=self.user, author=self.author,
            title="T", content="C", status="DRAFT",
        )
        url = reverse("blogpostmodel-detail", args=[post.id])
        res = self.client.patch(url, {"status": "PUBLISHED"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.status, "PUBLISHED")

    def test_status_in_list_response(self):
        BlogPostModel.objects.create(
            user=self.user, author=self.author,
            title="T", content="C", status="DRAFT",
        )
        res = self.client.get(POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("status", res.data[0])
