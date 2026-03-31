from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from author.models import NewsletterSubscription

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


class NewsletterSubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subscriber = make_user("subscriber")
        self.author = make_user("newsletter_author")

    def test_subscribe_returns_201(self):
        self.client.force_authenticate(user=self.subscriber)
        res = self.client.post(f"/api/users/{self.author.id}/subscribe/")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NewsletterSubscription.objects.filter(
            subscriber=self.subscriber, author=self.author).exists())

    def test_unsubscribe_returns_204(self):
        NewsletterSubscription.objects.create(subscriber=self.subscriber, author=self.author)
        self.client.force_authenticate(user=self.subscriber)
        res = self.client.delete(f"/api/users/{self.author.id}/subscribe/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NewsletterSubscription.objects.filter(
            subscriber=self.subscriber, author=self.author).exists())

    def test_self_subscribe_returns_400(self):
        self.client.force_authenticate(user=self.author)
        res = self.client.post(f"/api/users/{self.author.id}/subscribe/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_subscribe_returns_200(self):
        NewsletterSubscription.objects.create(subscriber=self.subscriber, author=self.author)
        self.client.force_authenticate(user=self.subscriber)
        res = self.client.post(f"/api/users/{self.author.id}/subscribe/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_subscribe_requires_auth(self):
        res = self.client.post(f"/api/users/{self.author.id}/subscribe/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_subscriptions(self):
        NewsletterSubscription.objects.create(subscriber=self.subscriber, author=self.author)
        self.client.force_authenticate(user=self.subscriber)
        res = self.client.get("/api/subscriptions/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_subscriber_count_in_stats(self):
        NewsletterSubscription.objects.create(subscriber=self.subscriber, author=self.author)
        res = self.client.get(f"/api/users/{self.author.id}/stats/")
        self.assertIn("subscriber_count", res.data)
        self.assertEqual(res.data["subscriber_count"], 1)
