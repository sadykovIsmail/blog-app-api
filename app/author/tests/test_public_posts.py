from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from author.models import AuthorModel, BlogPostModel, Category, Tag

User = get_user_model()

PUBLIC_POSTS_URL = reverse('public-post-list')


def create_user(username='user', password='pass12345'):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name='Author', email='a@example.com')


class TestPublicPosts(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)

    def _create_post(self, title='Post', status_val='published'):
        return BlogPostModel.objects.create(
            title=title, content='Content here', user=self.user,
            author=self.author, status=status_val,
        )

    def test_public_can_list_published_posts(self):
        self._create_post('Published Post', 'published')
        self._create_post('Draft Post', 'draft')
        res = self.client.get(PUBLIC_POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['title'], 'Published Post')

    def test_public_cannot_see_drafts(self):
        self._create_post('Draft', 'draft')
        res = self.client.get(PUBLIC_POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 0)

    def test_public_can_retrieve_by_slug(self):
        post = self._create_post('Slug Post', 'published')
        url = reverse('public-post-detail', args=[post.slug])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['slug'], post.slug)

    def test_published_post_has_auto_slug(self):
        post = self._create_post('My Awesome Post', 'published')
        self.assertEqual(post.slug, 'my-awesome-post')

    def test_slug_uniqueness(self):
        post1 = self._create_post('Same Title', 'published')
        post2 = self._create_post('Same Title', 'published')
        self.assertNotEqual(post1.slug, post2.slug)
        self.assertEqual(post2.slug, 'same-title-1')

    def test_reading_time_calculated(self):
        # 200 words should give 1 minute reading time
        content = ' '.join(['word'] * 200)
        post = BlogPostModel.objects.create(
            title='Long Post', content=content, user=self.user,
            author=self.author, status='published',
        )
        self.assertEqual(post.reading_time, 1)

    def test_reading_time_longer_content(self):
        # 600 words should give 3 minutes reading time
        content = ' '.join(['word'] * 600)
        post = BlogPostModel.objects.create(
            title='Very Long Post', content=content, user=self.user,
            author=self.author, status='published',
        )
        self.assertEqual(post.reading_time, 3)

    def test_public_can_read_without_auth(self):
        self._create_post('Open Post', 'published')
        res = self.client.get(PUBLIC_POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_by_category(self):
        cat = Category.objects.create(name='Tech')
        post1 = self._create_post('Tech Post', 'published')
        post1.category = cat
        post1.save()
        self._create_post('Other Post', 'published')
        res = self.client.get(PUBLIC_POSTS_URL + f'?category={cat.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_filter_by_tags(self):
        tag = Tag.objects.create(name='python')
        post = self._create_post('Python Post', 'published')
        post.tags.add(tag)
        self._create_post('Other Post', 'published')
        res = self.client.get(PUBLIC_POSTS_URL + f'?tags={tag.slug}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_search_by_title(self):
        self._create_post('Django Tutorial', 'published')
        self._create_post('React Basics', 'published')
        res = self.client.get(PUBLIC_POSTS_URL + '?search=django')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_pagination_works(self):
        for i in range(15):
            self._create_post(f'Post {i}', 'published')
        res = self.client.get(PUBLIC_POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 15)
        self.assertEqual(len(res.data['results']), 10)
        self.assertIsNotNone(res.data['next'])

    def test_pagination_second_page(self):
        for i in range(15):
            self._create_post(f'Post {i}', 'published')
        res = self.client.get(PUBLIC_POSTS_URL + '?page=2')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 5)
