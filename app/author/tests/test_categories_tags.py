from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from author.models import Category, Tag, BlogPostModel, AuthorModel

User = get_user_model()

CATEGORIES_URL = reverse('category-list')
TAGS_URL = reverse('tag-list')


def create_user(username='testuser', password='testpass123'):
    return User.objects.create_user(username=username, password=password)


def create_author(user, name='Author', email='author@example.com'):
    return AuthorModel.objects.create(user=user, name=name, email=email)


class TestCategoryEndpoints(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='adminpass123')
        self.user = create_user()

    def test_anyone_can_list_categories(self):
        Category.objects.create(name='Django')
        res = self.client.get(CATEGORIES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_can_create_category(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(CATEGORIES_URL, {'name': 'Python', 'description': 'Python stuff'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Python').exists())

    def test_slug_auto_generated(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(CATEGORIES_URL, {'name': 'Web Development'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cat = Category.objects.get(name='Web Development')
        self.assertEqual(cat.slug, 'web-development')

    def test_regular_user_cannot_create_category(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(CATEGORIES_URL, {'name': 'Unauthorized'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_category(self):
        res = self.client.post(CATEGORIES_URL, {'name': 'NoAuth'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_category_fails(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(CATEGORIES_URL, {'name': 'Unique'})
        res = self.client.post(CATEGORIES_URL, {'name': 'Unique'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_count_reflects_published_only(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(CATEGORIES_URL, {'name': 'Tech'})
        cat = Category.objects.get(name='Tech')
        author = create_author(self.user)
        BlogPostModel.objects.create(
            title='Draft', content='c', user=self.user,
            author=author, category=cat, status='draft',
        )
        BlogPostModel.objects.create(
            title='Published', content='c', user=self.user,
            author=author, category=cat, status='published',
        )
        res = self.client.get(reverse('category-detail', kwargs={'slug': cat.slug}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['post_count'], 1)


class TestTagEndpoints(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='adminpass123')
        self.user = create_user()

    def test_anyone_can_list_tags(self):
        Tag.objects.create(name='python')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_can_create_tag(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(TAGS_URL, {'name': 'Django REST'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name='Django REST').exists())

    def test_tag_slug_auto_generated(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(TAGS_URL, {'name': 'Machine Learning'})
        tag = Tag.objects.get(name='Machine Learning')
        self.assertEqual(tag.slug, 'machine-learning')

    def test_regular_user_cannot_create_tag(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(TAGS_URL, {'name': 'nope'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_tags(self):
        self.client.force_authenticate(user=self.admin)
        Tag.objects.create(name='python')
        Tag.objects.create(name='javascript')
        res = self.client.get(TAGS_URL + '?search=python')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data['results']
        self.assertTrue(any(t['name'] == 'python' for t in results))
        self.assertFalse(any(t['name'] == 'javascript' for t in results))
