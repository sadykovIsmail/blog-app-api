from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel, Tag

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


def make_post(user, title="Test", status_val="PUBLISHED"):
    author = AuthorModel.objects.create(name="A", email="a@a.com", user=user)
    return BlogPostModel.objects.create(
        title=title, content="content", author=author, user=user,
        status=status_val, visibility="PUBLIC",
    )


class TagTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("tagger")
        self.client.force_authenticate(user=self.user)
        self.post = make_post(self.user)

    def test_create_tag(self):
        res = self.client.post("/api/tags/", {"name": "python"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name="python").exists())

    def test_tag_slug_auto_generated(self):
        res = self.client.post("/api/tags/", {"name": "Machine Learning"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["slug"], "machine-learning")

    def test_list_tags(self):
        Tag.objects.create(name="django", slug="django")
        Tag.objects.create(name="react", slug="react")
        res = self.client.get("/api/tags/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 2)

    def test_add_tag_to_post(self):
        tag = Tag.objects.create(name="python", slug="python")
        res = self.client.post(f"/api/posts/{self.post.id}/tags/", {"tag_id": tag.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag, self.post.tags.all())

    def test_remove_tag_from_post(self):
        tag = Tag.objects.create(name="python", slug="python")
        self.post.tags.add(tag)
        res = self.client.delete(f"/api/posts/{self.post.id}/tags/{tag.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(tag, self.post.tags.all())

    def test_filter_posts_by_tag(self):
        tag = Tag.objects.create(name="python", slug="python")
        self.post.tags.add(tag)
        res = self.client.get(f"/api/public/posts/?tag=python")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_post_tags_in_response(self):
        tag = Tag.objects.create(name="python", slug="python")
        self.post.tags.add(tag)
        res = self.client.get(f"/api/public/posts/")
        tags = res.data["results"][0].get("tags", [])
        self.assertTrue(any(t["slug"] == "python" for t in tags))

    def test_duplicate_tag_returns_400(self):
        Tag.objects.create(name="python", slug="python")
        res = self.client.post("/api/tags/", {"name": "python"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
