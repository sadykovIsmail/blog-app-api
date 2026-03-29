from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Comment

User = get_user_model()


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def create_post(user, author):
    return BlogPostModel.objects.create(
        user=user, author=author, title="Post", content="body",
        status="PUBLISHED", visibility="PUBLIC",
    )


def comments_url(post_id):
    return reverse("post-comments", args=[post_id])


class CommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("commenter")
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        res = self.client.post(comments_url(self.post.id), {"body": "Great post!"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["body"], "Great post!")

    def test_comment_requires_auth(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(comments_url(self.post.id), {"body": "hello"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reply_to_comment(self):
        parent = Comment.objects.create(post=self.post, user=self.user, body="Parent")
        res = self.client.post(
            comments_url(self.post.id),
            {"body": "Reply", "parent": parent.id},
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["parent"], parent.id)

    def test_list_comments_for_post(self):
        Comment.objects.create(post=self.post, user=self.user, body="First")
        res = self.client.get(comments_url(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_owner_can_delete_comment(self):
        comment = Comment.objects.create(post=self.post, user=self.user, body="Mine")
        url = reverse("comment-detail", args=[comment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_comment(self):
        other = create_user("other")
        comment = Comment.objects.create(post=self.post, user=other, body="Theirs")
        url = reverse("comment-detail", args=[comment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_edit_comment(self):
        comment = Comment.objects.create(post=self.post, user=self.user, body="Old")
        url = reverse("comment-detail", args=[comment.id])
        res = self.client.patch(url, {"body": "Updated"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "Updated")

    def test_comment_body_required(self):
        res = self.client.post(comments_url(self.post.id), {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
