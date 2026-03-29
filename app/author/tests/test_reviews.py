from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@t.com")


def create_post(user, author, post_status="DRAFT"):
    return BlogPostModel.objects.create(
        user=user, author=author, title="Post", content="body", status=post_status,
    )


def reviews_url(post_id):
    return reverse("post-reviews", args=[post_id])


class ReviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author_user = create_user("reviewauthor")
        self.reviewer = create_user("reviewer")
        self.author = create_author(self.author_user)
        self.post = create_post(self.author_user, self.author)
        self.reviewer_client = APIClient()
        self.reviewer_client.force_authenticate(user=self.reviewer)
        self.client.force_authenticate(user=self.author_user)

    def test_submit_review(self):
        res = self.reviewer_client.post(reviews_url(self.post.id), {
            "rating": 4, "notes": "Great structure, minor grammar issues.",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_review_requires_rating_1_to_5(self):
        res = self.reviewer_client.post(reviews_url(self.post.id), {
            "rating": 6, "notes": "Out of range",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_rating_minimum_1(self):
        res = self.reviewer_client.post(reviews_url(self.post.id), {
            "rating": 0, "notes": "Too low",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_can_list_reviews(self):
        self.reviewer_client.post(reviews_url(self.post.id), {"rating": 3, "notes": "OK"})
        res = self.client.get(reviews_url(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_reviewer_cannot_review_own_posts(self):
        own_post = create_post(self.reviewer, create_author(self.reviewer))
        res = self.reviewer_client.post(reviews_url(own_post.id), {
            "rating": 5, "notes": "Self-review",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_requires_auth(self):
        anon = APIClient()
        res = anon.post(reviews_url(self.post.id), {"rating": 3, "notes": "anon"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_fields_in_response(self):
        res = self.reviewer_client.post(reviews_url(self.post.id), {
            "rating": 5, "notes": "Excellent",
        })
        for field in ["id", "rating", "notes", "reviewer", "created_at"]:
            self.assertIn(field, res.data)
