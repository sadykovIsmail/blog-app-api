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
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@test.com")


class PostVisibilityFieldTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("visuser")
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_default_visibility_is_public(self):
        payload = {"title": "My Post", "content": "hello", "author": self.author.id}
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["visibility"], "PUBLIC")

    def test_can_set_unlisted_visibility(self):
        payload = {
            "title": "Unlisted", "content": "x",
            "author": self.author.id, "visibility": "UNLISTED",
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["visibility"], "UNLISTED")

    def test_invalid_visibility_returns_400(self):
        payload = {
            "title": "Bad", "content": "x",
            "author": self.author.id, "visibility": "SECRET",
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_visibility_in_list_response(self):
        BlogPostModel.objects.create(
            user=self.user, author=self.author,
            title="T", content="C",
        )
        res = self.client.get(POSTS_URL)
        self.assertIn("visibility", res.data[0])

    def test_can_update_visibility(self):
        post = BlogPostModel.objects.create(
            user=self.user, author=self.author, title="T", content="C",
        )
        url = reverse("blogpostmodel-detail", args=[post.id])
        res = self.client.patch(url, {"visibility": "UNLISTED"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.visibility, "UNLISTED")
