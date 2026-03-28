from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()
REGISTER_URL = reverse("register")


class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_returns_id_username_email(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertIn("id", res.data)
        self.assertEqual(res.data["username"], "newuser")
        self.assertEqual(res.data["email"], "newuser@example.com")
        self.assertNotIn("password", res.data)

    def test_register_password_is_hashed(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123",
        }
        self.client.post(REGISTER_URL, payload)
        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("StrongPass123"))

    def test_register_duplicate_username_returns_400(self):
        User.objects.create_user(username="taken", email="taken@example.com", password="pass")
        payload = {
            "username": "taken",
            "email": "other@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_returns_400(self):
        User.objects.create_user(username="user1", email="dupe@example.com", password="pass")
        payload = {
            "username": "user2",
            "email": "dupe@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username_returns_400(self):
        payload = {"email": "x@example.com", "password": "StrongPass123"}
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password_returns_400(self):
        payload = {"username": "x", "email": "x@example.com"}
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_no_auth_required(self):
        """Registration must be accessible without a token."""
        payload = {
            "username": "anonuser",
            "email": "anon@example.com",
            "password": "StrongPass123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
