from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='rssuser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_published_post(user, title='RSS Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Content for RSS feed test post.',
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
        published_at=timezone.now(),
    )
    return post


class RSSFeedTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()

    def test_get_feed_returns_200(self):
        """GET /feed/ returns 200."""
        response = self.client.get('/feed/')
        self.assertEqual(response.status_code, 200)

    def test_feed_content_type_is_xml(self):
        """Response contains Content-Type with xml."""
        response = self.client.get('/feed/')
        self.assertIn('xml', response['Content-Type'])

    def test_get_nonexistent_author_feed_returns_404(self):
        """GET /feed/nonexistent/ returns 404."""
        response = self.client.get('/feed/nonexistenthandle/')
        self.assertEqual(response.status_code, 404)

    def test_feed_contains_post_titles(self):
        """Feed contains post titles."""
        post = make_published_post(self.user, title='My Great RSS Post')
        response = self.client.get('/feed/')
        content = response.content.decode('utf-8')
        self.assertIn('My Great RSS Post', content)

    def test_feed_has_item_when_published_post_exists(self):
        """GET /feed/ has at least one item when published post exists."""
        make_published_post(self.user, title='Feed Item Post')
        response = self.client.get('/feed/')
        content = response.content.decode('utf-8')
        self.assertIn('Feed Item Post', content)
