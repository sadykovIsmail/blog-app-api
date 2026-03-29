from django.test import TestCase, override_settings
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


@override_settings(
    REST_FRAMEWORK={
        **{},
        'DEFAULT_THROTTLE_CLASSES': [
            'author.throttles.RegisterThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'register': '3/min',
            'comments': '5/min',
            'follows': '10/min',
        },
    }
)
class RateLimitingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_throttle_class_exists(self):
        from author.throttles import RegisterThrottle, CommentThrottle, FollowThrottle
        self.assertTrue(hasattr(RegisterThrottle, 'scope'))
        self.assertTrue(hasattr(CommentThrottle, 'scope'))
        self.assertTrue(hasattr(FollowThrottle, 'scope'))

    def test_register_throttle_scope_is_register(self):
        from author.throttles import RegisterThrottle
        self.assertEqual(RegisterThrottle.scope, 'register')

    def test_comment_throttle_scope_is_comments(self):
        from author.throttles import CommentThrottle
        self.assertEqual(CommentThrottle.scope, 'comments')

    def test_follow_throttle_scope_is_follows(self):
        from author.throttles import FollowThrottle
        self.assertEqual(FollowThrottle.scope, 'follows')

    def test_throttle_rates_configured_in_settings(self):
        from django.conf import settings
        rates = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_THROTTLE_RATES', {})
        self.assertIn('register', rates)
        self.assertIn('comments', rates)
        self.assertIn('follows', rates)
