from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Follow, Reaction, Comment

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


def make_post(user, title="Stats Post"):
    author = AuthorModel.objects.create(name="A", email=f"{title[:5]}@a.com", user=user)
    return BlogPostModel.objects.create(
        title=title, content="content", author=author, user=user,
        status="PUBLISHED", visibility="PUBLIC", published_at=timezone.now(),
    )


class UserStatsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("statsuser")
        self.other = make_user("other")

    def test_stats_endpoint_returns_200(self):
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_stats_no_auth_required(self):
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_total_posts(self):
        make_post(self.user, "Post 1")
        make_post(self.user, "Post 2")
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertEqual(res.data["total_posts"], 2)

    def test_stats_follower_count(self):
        Follow.objects.create(follower=self.other, following=self.user)
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertEqual(res.data["follower_count"], 1)

    def test_stats_following_count(self):
        Follow.objects.create(follower=self.user, following=self.other)
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertEqual(res.data["following_count"], 1)

    def test_stats_total_reactions(self):
        post = make_post(self.user, "Liked Post")
        Reaction.objects.create(user=self.other, post=post)
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertEqual(res.data["total_reactions"], 1)

    def test_stats_total_comments(self):
        post = make_post(self.user, "Commented Post")
        Comment.objects.create(post=post, user=self.other, body="nice")
        res = self.client.get(f"/api/users/{self.user.id}/stats/")
        self.assertEqual(res.data["total_comments"], 1)

    def test_stats_nonexistent_user_returns_404(self):
        res = self.client.get("/api/users/99999/stats/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
