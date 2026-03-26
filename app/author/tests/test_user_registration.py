from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

REGISTER_URL = reverse('register')
TOKEN_URL = reverse('token_obtain_pair')


class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user(self):
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch_fails(self):
        payload = {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password': 'securepass123',
            'password2': 'differentpass',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username_fails(self):
        User.objects.create_user(username='existinguser', password='pass12345')
        payload = {
            'username': 'existinguser',
            'email': 'other@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password_fails(self):
        payload = {
            'username': 'shortpwduser',
            'email': 'short@example.com',
            'password': 'abc',
            'password2': 'abc',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_user_profile(self):
        from author.models import UserProfile
        payload = {
            'username': 'profileuser',
            'email': 'profile@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='profileuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_registered_user_can_login(self):
        User.objects.create_user(username='logintest', password='securepass123')
        payload = {'username': 'logintest', 'password': 'securepass123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_register_without_username_fails(self):
        payload = {
            'email': 'nousername@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
