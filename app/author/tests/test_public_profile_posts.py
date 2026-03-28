from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def create_user(username, password="pass123", handle=None):
    user = User.objects.create_user(username=username, password=password)
    if handle:
        user.handle = handle
        user.save()
    return user


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@test.com")


def create_post(user, author, title="Post", post_status="PUBLISHED", visibility="PUBLIC"):
    return BlogPostModel.objects.create(
        user=user, author=author, title=title, content="body",
        status=post_status, visibility=visibility,
    )


class PublicProfilePostsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("pubauthor", handle="pubauthor")
        self.author = create_author(self.user)

    def _url(self, handle):
        return reverse("public-profile-posts", args=[handle])

    def test_returns_published_posts_for_handle(self):
        create_post(self.user, self.author, title="Visible Post")
        res = self.client.get(self._url("pubauthor"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in res.data["results"]]
        self.assertIn("Visible Post", titles)

    def test_excludes_draft_posts(self):
        create_post(self.user, self.author, title="Draft", post_status="DRAFT")
        res = self.client.get(self._url("pubauthor"))
        titles = [p["title"] for p in res.data["results"]]
        self.assertNotIn("Draft", titles)

    def test_excludes_unlisted_posts(self):
        create_post(self.user, self.author, title="Unlisted", visibility="UNLISTED")
        res = self.client.get(self._url("pubauthor"))
        titles = [p["title"] for p in res.data["results"]]
        self.assertNotIn("Unlisted", titles)

    def test_unknown_handle_returns_404(self):
        res = self.client.get(self._url("nobody"))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_auth_required(self):
        res = self.client.get(self._url("pubauthor"))
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_shows_that_users_posts(self):
        other = create_user("otheruser", handle="otheruser")
        other_author = create_author(other)
        create_post(self.user, self.author, title="My Post")
        create_post(other, other_author, title="Other Post")

        res = self.client.get(self._url("pubauthor"))
        titles = [p["title"] for p in res.data["results"]]
        self.assertIn("My Post", titles)
        self.assertNotIn("Other Post", titles)
