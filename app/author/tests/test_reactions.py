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


class ReactionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("reactor")
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.comment = Comment.objects.create(post=self.post, user=self.user, body="Nice")
        self.client.force_authenticate(user=self.user)

    def test_react_to_post(self):
        url = reverse("post-react", args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_react_to_comment(self):
        url = reverse("comment-react", args=[self.comment.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_reaction_count_on_post(self):
        url = reverse("post-react", args=[self.post.id])
        self.client.post(url)
        res = self.client.get(reverse("public-post-list"))
        post_data = next(p for p in res.data["results"] if p["id"] == self.post.id)
        self.assertIn("reaction_count", post_data)
        self.assertEqual(post_data["reaction_count"], 1)

    def test_reaction_toggles_off(self):
        url = reverse("post-react", args=[self.post.id])
        self.client.post(url)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_one_reaction_per_user_per_post(self):
        url = reverse("post-react", args=[self.post.id])
        self.client.post(url)
        self.client.post(url)
        other = create_user("other2")
        client2 = APIClient()
        client2.force_authenticate(user=other)
        client2.post(url)
        res = self.client.get(reverse("public-post-list"))
        post_data = next(p for p in res.data["results"] if p["id"] == self.post.id)
        self.assertEqual(post_data["reaction_count"], 1)

    def test_reaction_requires_auth(self):
        self.client.force_authenticate(user=None)
        url = reverse("post-react", args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
