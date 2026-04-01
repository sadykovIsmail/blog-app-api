from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class APIVersioningTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_v1_public_feed_accessible(self):
        res = self.client.get("/api/v1/public/posts/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_v1_register_accessible(self):
        res = self.client.post("/api/v1/auth/register/", {
            "username": "versionuser", "email": "v@v.com", "password": "pass1234"
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_v1_token_endpoint_accessible(self):
        User.objects.create_user(username="vuser2", email="v2@v.com", password="pass1234")
        res = self.client.post("/api/v1/token/", {"username": "vuser2", "password": "pass1234"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_old_api_still_works(self):
        """Original /api/ endpoints still respond."""
        res = self.client.get("/api/public/posts/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_v1_tags_accessible(self):
        res = self.client.get("/api/v1/tags/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_v1_trending_accessible(self):
        res = self.client.get("/api/v1/public/posts/trending/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
