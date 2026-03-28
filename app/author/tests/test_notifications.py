from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Comment, Notification

User = get_user_model()
NOTIFICATIONS_URL = reverse("notifications")


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def create_post(user, author, post_status="PUBLISHED"):
    return BlogPostModel.objects.create(
        user=user, author=author, title="Post", content="body",
        status=post_status, visibility="PUBLIC",
    )


class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author_user = create_user("author")
        self.follower_user = create_user("follower")
        self.author = create_author(self.author_user)
        self.client.force_authenticate(user=self.follower_user)

    def test_follow_creates_notification_for_target(self):
        self.client.post(reverse("follow", args=[self.author_user.id]))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author_user,
                notification_type="follow",
            ).exists()
        )

    def test_comment_creates_notification_for_post_author(self):
        post = create_post(self.author_user, self.author)
        self.client.post(reverse("post-comments", args=[post.id]), {"body": "Nice!"})
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author_user,
                notification_type="comment",
            ).exists()
        )

    def test_reply_creates_notification_for_comment_author(self):
        post = create_post(self.author_user, self.author)
        parent = Comment.objects.create(post=post, user=self.author_user, body="Parent")
        self.client.post(
            reverse("post-comments", args=[post.id]),
            {"body": "Reply", "parent": parent.id},
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author_user,
                notification_type="reply",
            ).exists()
        )

    def test_get_notifications_returns_own(self):
        Notification.objects.create(
            recipient=self.follower_user,
            notification_type="follow",
        )
        res = self.client.get(NOTIFICATIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_notifications_include_unread_count(self):
        Notification.objects.create(
            recipient=self.follower_user,
            notification_type="follow",
        )
        res = self.client.get(NOTIFICATIONS_URL)
        self.assertIn("unread_count", res.data)
        self.assertEqual(res.data["unread_count"], 1)

    def test_notifications_requires_auth(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(NOTIFICATIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
