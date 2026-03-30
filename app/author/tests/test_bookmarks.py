from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Bookmark

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


def make_post(user, title="Post"):
    author = AuthorModel.objects.create(name="A", email="a@a.com", user=user)
    return BlogPostModel.objects.create(
        title=title, content="content", author=author, user=user,
        status="PUBLISHED", visibility="PUBLIC",
    )


class BookmarkTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("reader")
        self.author = make_user("author")
        self.client.force_authenticate(user=self.user)
        self.post = make_post(self.author)

    def test_bookmark_post(self):
        res = self.client.post(f"/api/posts/{self.post.id}/bookmark/")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Bookmark.objects.filter(user=self.user, post=self.post).exists())

    def test_unbookmark_post(self):
        Bookmark.objects.create(user=self.user, post=self.post)
        res = self.client.delete(f"/api/posts/{self.post.id}/bookmark/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Bookmark.objects.filter(user=self.user, post=self.post).exists())

    def test_list_bookmarks(self):
        Bookmark.objects.create(user=self.user, post=self.post)
        res = self.client.get("/api/bookmarks/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_duplicate_bookmark_returns_200(self):
        Bookmark.objects.create(user=self.user, post=self.post)
        res = self.client.post(f"/api/posts/{self.post.id}/bookmark/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unbookmark_non_existing_returns_404(self):
        res = self.client.delete(f"/api/posts/{self.post.id}/bookmark/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_bookmarks_require_auth(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/bookmarks/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bookmark_count_in_feed(self):
        Bookmark.objects.create(user=self.user, post=self.post)
        res = self.client.get("/api/bookmarks/")
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], self.post.title)
