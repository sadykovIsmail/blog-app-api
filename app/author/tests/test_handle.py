from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()
REGISTER_URL = reverse("register")


class HandleFieldTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_register_returns_handle(self):
        payload = {
            "username": "handleuser",
            "email": "handle@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("handle", res.data)

    def test_handle_defaults_to_username(self):
        payload = {
            "username": "defaulthandle",
            "email": "dh@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.data["handle"], "defaulthandle")

    def test_handle_is_unique(self):
        User.objects.create_user(
            username="user1", email="u1@example.com",
            password="pass", handle="takenhandle",
        )
        User.objects.create_user(
            username="user2", email="u2@example.com",
            password="pass", handle="takenhandle2",
        )
        user = User.objects.get(username="user1")
        self.assertEqual(user.handle, "takenhandle")

    def test_profile_endpoint_exposes_handle(self):
        url = reverse("profile")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("handle", res.data)

    def test_can_update_handle(self):
        url = reverse("profile")
        res = self.client.patch(url, {"handle": "mynewhandle"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.handle, "mynewhandle")

    def test_duplicate_handle_update_returns_400(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass",
        )
        other.handle = "taken"
        other.save()

        url = reverse("profile")
        res = self.client.patch(url, {"handle": "taken"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
