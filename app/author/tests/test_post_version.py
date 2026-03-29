from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, PostVersion

User = get_user_model()
POSTS_URL = reverse("blogpostmodel-list")


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


class PostVersionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("versioner")
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_version_created_on_post_update(self):
        res = self.client.post(POSTS_URL, {
            "title": "Original", "content": "First content", "author": self.author.id,
        })
        post_id = res.data["id"]
        url = reverse("blogpostmodel-detail", args=[post_id])
        self.client.patch(url, {"title": "Updated", "reason_for_change": "Fixed typo"})
        self.assertEqual(PostVersion.objects.filter(post_id=post_id).count(), 1)

    def test_version_snapshot_contains_old_content(self):
        res = self.client.post(POSTS_URL, {
            "title": "Original", "content": "First content", "author": self.author.id,
        })
        post_id = res.data["id"]
        url = reverse("blogpostmodel-detail", args=[post_id])
        self.client.patch(url, {"title": "Updated"})
        version = PostVersion.objects.get(post_id=post_id)
        self.assertEqual(version.title_snapshot, "Original")
        self.assertEqual(version.content_snapshot, "First content")

    def test_version_stores_reason_for_change(self):
        res = self.client.post(POSTS_URL, {
            "title": "T", "content": "C", "author": self.author.id,
        })
        post_id = res.data["id"]
        url = reverse("blogpostmodel-detail", args=[post_id])
        self.client.patch(url, {"title": "New T", "reason_for_change": "Added more detail"})
        version = PostVersion.objects.get(post_id=post_id)
        self.assertEqual(version.reason_for_change, "Added more detail")

    def test_multiple_updates_create_multiple_versions(self):
        res = self.client.post(POSTS_URL, {
            "title": "T", "content": "C", "author": self.author.id,
        })
        post_id = res.data["id"]
        url = reverse("blogpostmodel-detail", args=[post_id])
        self.client.patch(url, {"title": "V2"})
        self.client.patch(url, {"title": "V3"})
        self.assertEqual(PostVersion.objects.filter(post_id=post_id).count(), 2)

    def test_version_has_version_number(self):
        res = self.client.post(POSTS_URL, {
            "title": "T", "content": "C", "author": self.author.id,
        })
        post_id = res.data["id"]
        url = reverse("blogpostmodel-detail", args=[post_id])
        self.client.patch(url, {"title": "V2"})
        self.client.patch(url, {"title": "V3"})
        versions = PostVersion.objects.filter(post_id=post_id).order_by("version_number")
        self.assertEqual(versions[0].version_number, 1)
        self.assertEqual(versions[1].version_number, 2)
