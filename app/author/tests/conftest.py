"""
pytest fixtures shared across all test modules.

Import these in test files via standard pytest fixture injection — no import needed,
pytest auto-discovers conftest.py fixtures in the same directory and parent directories.
"""
import pytest
from rest_framework.test import APIClient

from author.tests.factories import (
    UserFactory,
    AuthorModelFactory,
    BlogPostFactory,
    PublishedPostFactory,
    CommentFactory,
    TagFactory,
    BookmarkFactory,
    FollowFactory,
    NotificationFactory,
)


@pytest.fixture
def api_client():
    """Unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def user(db):
    """A regular authenticated user."""
    return UserFactory()


@pytest.fixture
def other_user(db):
    """A second user (for ownership / permission tests)."""
    return UserFactory()


@pytest.fixture
def auth_client(user):
    """DRF test client authenticated as `user`."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def post(db, user):
    """A draft blog post owned by `user`."""
    author = AuthorModelFactory(user=user)
    return BlogPostFactory(user=user, author=author)


@pytest.fixture
def published_post(db, user):
    """A published, public blog post owned by `user`."""
    author = AuthorModelFactory(user=user)
    return PublishedPostFactory(user=user, author=author)


@pytest.fixture
def comment(db, published_post, other_user):
    """A comment on `published_post` written by `other_user`."""
    return CommentFactory(post=published_post, user=other_user)


@pytest.fixture
def tag(db):
    """A single tag."""
    return TagFactory()


@pytest.fixture
def bookmark(db, user, published_post):
    """A bookmark by `user` on `published_post`."""
    return BookmarkFactory(user=user, post=published_post)


@pytest.fixture
def follow(db, user, other_user):
    """user follows other_user."""
    return FollowFactory(follower=user, following=other_user)


@pytest.fixture
def unread_notification(db, user, other_user):
    """An unread notification for `user`."""
    return NotificationFactory(recipient=user, actor=other_user, notification_type="follow")
