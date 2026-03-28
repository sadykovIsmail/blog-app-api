from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel

User = get_user_model()
PUBLIC_FEED_URL = reverse("public-post-list")


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


def create_author(user):
    return AuthorModel.objects.create(user=user, name=user.username, email=f"{user.username}@test.com")


def create_post(user, author, title, content="body", days_ago=0):
    post = BlogPostModel.objects.create(
        user=user, author=author, title=title, content=content,
        status="PUBLISHED", visibility="PUBLIC",
    )
    if days_ago:
        BlogPostModel.objects.filter(pk=post.pk).update(
            published_at=timezone.now() - timezone.timedelta(days=days_ago)
        )
    return post


class SearchOrderingPaginationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("searchuser")
        self.author = create_author(self.user)

    def test_search_by_title(self):
        create_post(self.user, self.author, title="Django Tips")
        create_post(self.user, self.author, title="Python Tricks")
        res = self.client.get(PUBLIC_FEED_URL, {"search": "Django"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p["title"] for p in res.data["results"]]
        self.assertIn("Django Tips", titles)
        self.assertNotIn("Python Tricks", titles)

    def test_search_by_content(self):
        create_post(self.user, self.author, title="Post A", content="advanced queries")
        create_post(self.user, self.author, title="Post B", content="hello world")
        res = self.client.get(PUBLIC_FEED_URL, {"search": "advanced queries"})
        titles = [p["title"] for p in res.data["results"]]
        self.assertIn("Post A", titles)
        self.assertNotIn("Post B", titles)

    def test_ordering_by_published_at_asc(self):
        create_post(self.user, self.author, title="Old Post", days_ago=5)
        create_post(self.user, self.author, title="New Post", days_ago=1)
        res = self.client.get(PUBLIC_FEED_URL, {"ordering": "published_at"})
        titles = [p["title"] for p in res.data["results"]]
        self.assertLess(titles.index("Old Post"), titles.index("New Post"))

    def test_ordering_by_published_at_desc(self):
        create_post(self.user, self.author, title="Old Post", days_ago=5)
        create_post(self.user, self.author, title="New Post", days_ago=1)
        res = self.client.get(PUBLIC_FEED_URL, {"ordering": "-published_at"})
        titles = [p["title"] for p in res.data["results"]]
        self.assertLess(titles.index("New Post"), titles.index("Old Post"))

    def test_pagination_page_size(self):
        for i in range(25):
            create_post(self.user, self.author, title=f"Post {i}")
        res = self.client.get(PUBLIC_FEED_URL, {"page_size": 5})
        self.assertEqual(len(res.data["results"]), 5)
        self.assertEqual(res.data["count"], 25)

    def test_pagination_second_page(self):
        for i in range(15):
            create_post(self.user, self.author, title=f"Post {i}")
        res = self.client.get(PUBLIC_FEED_URL, {"page": 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(res.data["results"]), 10)
