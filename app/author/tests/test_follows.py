from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


def create_user(username):
    return User.objects.create_user(username=username, password="pass123")


class FollowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("follower")
        self.target = create_user("target")
        self.client.force_authenticate(user=self.user)

    def _follow_url(self, user_id):
        return reverse("follow", args=[user_id])

    def _unfollow_url(self, user_id):
        return reverse("unfollow", args=[user_id])

    def test_follow_user(self):
        res = self.client.post(self._follow_url(self.target.id))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_follow_increments_follower_count(self):
        self.client.post(self._follow_url(self.target.id))
        url = reverse("profile-detail", args=[self.target.id])
        res = self.client.get(url)
        self.assertEqual(res.data["follower_count"], 1)

    def test_follow_increments_following_count(self):
        self.client.post(self._follow_url(self.target.id))
        url = reverse("profile-detail", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.data["following_count"], 1)

    def test_duplicate_follow_returns_400(self):
        self.client.post(self._follow_url(self.target.id))
        res = self.client.post(self._follow_url(self.target.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_follow_self(self):
        res = self.client.post(self._follow_url(self.user.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_user(self):
        self.client.post(self._follow_url(self.target.id))
        res = self.client.delete(self._unfollow_url(self.target.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_unfollow_decrements_follower_count(self):
        self.client.post(self._follow_url(self.target.id))
        self.client.delete(self._unfollow_url(self.target.id))
        url = reverse("profile-detail", args=[self.target.id])
        res = self.client.get(url)
        self.assertEqual(res.data["follower_count"], 0)

    def test_unfollow_non_followed_returns_400(self):
        res = self.client.delete(self._unfollow_url(self.target.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_requires_auth(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(self._follow_url(self.target.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
