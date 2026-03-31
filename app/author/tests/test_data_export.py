from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Comment, Bookmark, Follow

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


def make_post(user, title="Post"):
    author = AuthorModel.objects.create(name="A", email="a@a.com", user=user)
    return BlogPostModel.objects.create(
        title=title, content="content", author=author, user=user,
        status="PUBLISHED", visibility="PUBLIC",
    )


class DataExportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("exporter")
        self.other = make_user("other")
        self.client.force_authenticate(user=self.user)

    def test_export_returns_200(self):
        res = self.client.get("/api/auth/export/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_export_contains_posts_key(self):
        make_post(self.user, "My Post")
        res = self.client.get("/api/auth/export/")
        self.assertIn("posts", res.data)
        self.assertEqual(len(res.data["posts"]), 1)

    def test_export_contains_comments_key(self):
        post = make_post(self.other)
        Comment.objects.create(post=post, user=self.user, body="hello")
        res = self.client.get("/api/auth/export/")
        self.assertIn("comments", res.data)
        self.assertEqual(len(res.data["comments"]), 1)

    def test_export_contains_bookmarks_key(self):
        post = make_post(self.other)
        Bookmark.objects.create(user=self.user, post=post)
        res = self.client.get("/api/auth/export/")
        self.assertIn("bookmarks", res.data)
        self.assertEqual(len(res.data["bookmarks"]), 1)

    def test_export_contains_follows_key(self):
        Follow.objects.create(follower=self.user, following=self.other)
        res = self.client.get("/api/auth/export/")
        self.assertIn("follows", res.data)
        self.assertIn(self.other.handle, res.data["follows"])

    def test_export_requires_auth(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/auth/export/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
