from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, PostVersion

User = get_user_model()


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def changelog_url(post_id):
    return reverse("post-changelog", args=[post_id])


class ChangelogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("cluser")
        self.author = create_author(self.user)
        self.post = BlogPostModel.objects.create(
            user=self.user, author=self.author,
            title="Original", content="Body",
            status="PUBLISHED", visibility="PUBLIC",
        )
        PostVersion.objects.create(
            post=self.post, version_number=1,
            title_snapshot="Original", content_snapshot="Body",
            reason_for_change="Initial publish",
        )

    def test_changelog_accessible_without_auth(self):
        res = self.client.get(changelog_url(self.post.id))
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_changelog_returns_versions(self):
        res = self.client.get(changelog_url(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_changelog_includes_expected_fields(self):
        res = self.client.get(changelog_url(self.post.id))
        entry = res.data[0]
        for field in ["version_number", "reason_for_change", "changed_at"]:
            self.assertIn(field, entry)

    def test_changelog_ordered_by_version_number(self):
        PostVersion.objects.create(
            post=self.post, version_number=2,
            title_snapshot="Updated", content_snapshot="New body",
            reason_for_change="Fixed errors",
        )
        res = self.client.get(changelog_url(self.post.id))
        numbers = [v["version_number"] for v in res.data]
        self.assertEqual(numbers, sorted(numbers))

    def test_changelog_404_for_unknown_post(self):
        res = self.client.get(changelog_url(99999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
