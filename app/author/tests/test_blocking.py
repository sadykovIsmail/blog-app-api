from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def make_user(username='blocker', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


class BlockingTests(TestCase):
    def setUp(self):
        self.user = make_user(username='blocker1')
        self.target = make_user(username='target1')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_block_user_returns_201(self):
        response = self.client.post(f'/api/users/{self.target.pk}/block/')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Blocked', response.data['detail'])

    def test_unblock_user_returns_204(self):
        self.client.post(f'/api/users/{self.target.pk}/block/')
        response = self.client.delete(f'/api/users/{self.target.pk}/block/')
        self.assertEqual(response.status_code, 204)

    def test_self_block_returns_400(self):
        response = self.client.post(f'/api/users/{self.user.pk}/block/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Cannot block yourself', response.data['detail'])

    def test_blocking_same_user_twice_is_idempotent(self):
        self.client.post(f'/api/users/{self.target.pk}/block/')
        response = self.client.post(f'/api/users/{self.target.pk}/block/')
        self.assertIn(response.status_code, [200, 201])

    def test_block_requires_auth(self):
        anon_client = APIClient()
        response = anon_client.post(f'/api/users/{self.target.pk}/block/')
        self.assertEqual(response.status_code, 401)
