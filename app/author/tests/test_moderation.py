from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Comment

User = get_user_model()


def create_user(username, is_staff=False):
    return User.objects.create_user(username=username, password="pass123", is_staff=is_staff)


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def create_post(user, author):
    return BlogPostModel.objects.create(
        user=user, author=author, title="Post", content="body",
        status="PUBLISHED", visibility="PUBLIC",
    )


class ModerationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("reporter")
        self.staff = create_user("staffmember", is_staff=True)
        self.author_user = create_user("postauthor")
        self.author = create_author(self.author_user)
        self.post = create_post(self.author_user, self.author)
        self.comment = Comment.objects.create(
            post=self.post, user=self.author_user, body="Offensive content",
        )
        self.client.force_authenticate(user=self.user)

    def test_user_can_report_post(self):
        url = reverse("report-post", args=[self.post.id])
        res = self.client.post(url, {"reason": "Spam content"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_report_comment(self):
        url = reverse("report-comment", args=[self.comment.id])
        res = self.client.post(url, {"reason": "Abusive"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_report_requires_auth(self):
        self.client.force_authenticate(user=None)
        url = reverse("report-post", args=[self.post.id])
        res = self.client.post(url, {"reason": "Spam"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_can_hide_comment(self):
        staff_client = APIClient()
        staff_client.force_authenticate(user=self.staff)
        url = reverse("hide-comment", args=[self.comment.id])
        res = staff_client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_hidden)

    def test_non_staff_cannot_hide_comment(self):
        url = reverse("hide-comment", args=[self.comment.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_hide_creates_audit_log(self):
        from author.models import ModerationAuditLog
        staff_client = APIClient()
        staff_client.force_authenticate(user=self.staff)
        url = reverse("hide-comment", args=[self.comment.id])
        staff_client.post(url)
        self.assertTrue(
            ModerationAuditLog.objects.filter(
                actor=self.staff, action="hide_comment",
            ).exists()
        )

    def test_report_requires_reason(self):
        url = reverse("report-post", args=[self.post.id])
        res = self.client.post(url, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
