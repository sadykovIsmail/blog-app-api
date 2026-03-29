from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel

User = get_user_model()
POSTS_URL = reverse("blogpostmodel-list")


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


class ContentLintingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("lintuser")
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_title_max_200_chars(self):
        payload = {
            "title": "x" * 201, "content": "body",
            "author": self.author.id,
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_title_200_chars_accepted(self):
        payload = {
            "title": "x" * 200, "content": "body",
            "author": self.author.id,
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_body_max_50000_chars(self):
        payload = {
            "title": "T", "content": "x" * 50001,
            "author": self.author.id,
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_body_50000_chars_accepted(self):
        payload = {
            "title": "T", "content": "x" * 50000,
            "author": self.author.id,
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_max_20_links_enforced_on_publish(self):
        links = " ".join([f"https://link{i}.com" for i in range(21)])
        payload = {
            "title": "T", "content": links,
            "author": self.author.id, "status": "PUBLISHED",
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_body_blocked_on_publish(self):
        payload = {
            "title": "T", "content": "   ",
            "author": self.author.id, "status": "PUBLISHED",
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_body_allowed_on_draft(self):
        payload = {
            "title": "T", "content": "   ",
            "author": self.author.id, "status": "DRAFT",
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
