from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='viewuser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_published_post(user, title='View Count Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Content for view count test post.',
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
        published_at=timezone.now(),
    )
    return post


def make_draft_post(user, title='Draft Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'draft{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Draft content.',
        author=author,
        user=user,
        status=BlogPostModel.Status.DRAFT,
    )
    return post


class PostViewCountTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()

    def test_post_view_returns_200_with_view_count(self):
        """POST /posts/:id/view/ returns 200 with view_count."""
        post = make_published_post(self.user)
        response = self.client.post(f'/api/posts/{post.pk}/view/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('view_count', response.data)

    def test_same_ip_does_not_double_count(self):
        """Same IP doesn't double-count."""
        post = make_published_post(self.user)
        self.client.post(f'/api/posts/{post.pk}/view/')
        self.client.post(f'/api/posts/{post.pk}/view/')
        response = self.client.post(f'/api/posts/{post.pk}/view/')
        self.assertEqual(response.data['view_count'], 1)

    def test_view_count_appears_in_public_feed(self):
        """View count appears in public feed response."""
        post = make_published_post(self.user)
        self.client.post(f'/api/posts/{post.pk}/view/')
        response = self.client.get('/api/public/posts/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', [])
        self.assertTrue(len(results) > 0)
        self.assertIn('view_count', results[0])

    def test_non_published_post_returns_404(self):
        """Non-published post returns 404."""
        post = make_draft_post(self.user)
        response = self.client.post(f'/api/posts/{post.pk}/view/')
        self.assertEqual(response.status_code, 404)
