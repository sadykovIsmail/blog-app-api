from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from author.models import UserProfile

User = get_user_model()

PROFILE_URL = reverse('profile')
LOGOUT_URL = reverse('logout')


def create_user(username='profileuser', password='pass12345'):
    return User.objects.create_user(username=username, password=password)


class TestUserProfile(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_profile_creates_if_not_exists(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_get_profile_returns_correct_user(self):
        UserProfile.objects.create(user=self.user, bio='My bio')
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], self.user.username)
        self.assertEqual(res.data['bio'], 'My bio')

    def test_update_bio(self):
        UserProfile.objects.create(user=self.user)
        res = self.client.patch(PROFILE_URL, {'bio': 'Updated bio'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['bio'], 'Updated bio')
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.bio, 'Updated bio')

    def test_update_website(self):
        UserProfile.objects.create(user=self.user)
        res = self.client.patch(PROFILE_URL, {'website': 'https://example.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['website'], 'https://example.com')

    def test_unauthenticated_cannot_view_profile(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_has_username_and_email(self):
        UserProfile.objects.create(user=self.user)
        res = self.client.get(PROFILE_URL)
        self.assertIn('username', res.data)
        self.assertIn('email', res.data)


class TestLogout(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user('logoutuser')

    def test_logout_requires_refresh_token(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(LOGOUT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        res = self.client.post(LOGOUT_URL, {'refresh': 'sometoken'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_invalid_token_fails(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(LOGOUT_URL, {'refresh': 'invalid.token.here'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
