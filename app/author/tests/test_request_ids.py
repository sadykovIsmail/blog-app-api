from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class RequestIdTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_response_has_x_request_id_header(self):
        res = self.client.get(reverse("public-post-list"))
        self.assertIn("X-Request-ID", res)

    def test_x_request_id_is_non_empty(self):
        res = self.client.get(reverse("public-post-list"))
        self.assertTrue(len(res["X-Request-ID"]) > 0)

    def test_each_request_gets_unique_id(self):
        res1 = self.client.get(reverse("public-post-list"))
        res2 = self.client.get(reverse("public-post-list"))
        self.assertNotEqual(res1["X-Request-ID"], res2["X-Request-ID"])

    def test_client_provided_request_id_is_echoed(self):
        res = self.client.get(
            reverse("public-post-list"),
            HTTP_X_REQUEST_ID="my-custom-id-123",
        )
        self.assertEqual(res["X-Request-ID"], "my-custom-id-123")
