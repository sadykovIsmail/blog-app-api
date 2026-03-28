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


def create_post(user, author):
    return BlogPostModel.objects.create(
        user=user, author=author, title="Post", content="body",
        status="PUBLISHED", visibility="PUBLIC",
    )


def citations_url(post_id):
    return reverse("post-citations", args=[post_id])


def citation_detail_url(citation_id):
    return reverse("citation-detail", args=[citation_id])


class CitationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("cituser")
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.client.force_authenticate(user=self.user)
        self.valid_payload = {
            "url": "https://example.com/article",
            "title": "Example Article",
            "publisher": "Example Publisher",
        }

    def test_create_citation(self):
        res = self.client.post(citations_url(self.post.id), self.valid_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["url"], "https://example.com/article")

    def test_citation_requires_url(self):
        res = self.client.post(citations_url(self.post.id), {"title": "No URL"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_citations_for_post(self):
        self.client.post(citations_url(self.post.id), self.valid_payload)
        res = self.client.get(citations_url(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_update_citation(self):
        res = self.client.post(citations_url(self.post.id), self.valid_payload)
        citation_id = res.data["id"]
        url = citation_detail_url(citation_id)
        res = self.client.patch(url, {"title": "Updated Title"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Updated Title")

    def test_delete_citation(self):
        res = self.client.post(citations_url(self.post.id), self.valid_payload)
        citation_id = res.data["id"]
        url = citation_detail_url(citation_id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_create_citation(self):
        other = create_user("other")
        client2 = APIClient()
        client2.force_authenticate(user=other)
        res = client2.post(citations_url(self.post.id), self.valid_payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_citation_has_accessed_at(self):
        res = self.client.post(citations_url(self.post.id), self.valid_payload)
        self.assertIn("accessed_at", res.data)
