from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='sitemapuser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_published_post(user, title='Sitemap Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Content for sitemap test post.',
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


class SitemapTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()

    def test_sitemap_returns_200(self):
        """GET /sitemap.xml returns 200."""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

    def test_sitemap_content_type_is_xml(self):
        """Response is XML (content-type contains xml)."""
        response = self.client.get('/sitemap.xml')
        self.assertIn('xml', response['Content-Type'])

    def test_sitemap_contains_post_slug_urls(self):
        """Sitemap contains post slug URLs."""
        post = make_published_post(self.user, title='Sitemap Slug Post')
        response = self.client.get('/sitemap.xml')
        content = response.content.decode('utf-8')
        self.assertIn(post.slug, content)

    def test_unpublished_posts_not_in_sitemap(self):
        """Unpublished posts not in sitemap."""
        draft = make_draft_post(self.user, title='Unpublished Draft')
        response = self.client.get('/sitemap.xml')
        content = response.content.decode('utf-8')
        self.assertNotIn(draft.slug, content)
