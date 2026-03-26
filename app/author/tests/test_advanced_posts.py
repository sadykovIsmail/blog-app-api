from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from author.models import AuthorModel, BlogPostModel, Tag, Category

User = get_user_model()

POSTS_URL = reverse('blogpostmodel-list')


def create_user(username='user', password='pass12345'):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name='Author', email='a@example.com')


class TestPostStatus(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_post_created_as_draft_by_default(self):
        payload = {'title': 'New Post', 'content': 'Content', 'author': self.author.id}
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'draft')

    def test_publish_action(self):
        post = BlogPostModel.objects.create(
            title='Draft Post', content='Content', user=self.user,
            author=self.author, status='draft',
        )
        url = reverse('blogpostmodel-publish', args=[post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'published')
        post.refresh_from_db()
        self.assertEqual(post.status, 'published')

    def test_unpublish_action(self):
        post = BlogPostModel.objects.create(
            title='Published', content='Content', user=self.user,
            author=self.author, status='published',
        )
        url = reverse('blogpostmodel-unpublish', args=[post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'draft')

    def test_cannot_publish_other_users_post(self):
        other_user = create_user('other', 'pass12345')
        other_author = create_author(other_user)
        post = BlogPostModel.objects.create(
            title='Other Post', content='Content', user=other_user,
            author=other_author, status='draft',
        )
        url = reverse('blogpostmodel-publish', args=[post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class TestPostTags(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_post_with_tags(self):
        tag1 = Tag.objects.create(name='python')
        tag2 = Tag.objects.create(name='django')
        payload = {
            'title': 'Tagged Post',
            'content': 'Content',
            'author': self.author.id,
            'tag_ids': [tag1.id, tag2.id],
        }
        res = self.client.post(POSTS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = BlogPostModel.objects.get(id=res.data['id'])
        self.assertEqual(post.tags.count(), 2)

    def test_post_tags_displayed_in_response(self):
        tag = Tag.objects.create(name='flask')
        payload = {
            'title': 'Flask Post',
            'content': 'Content',
            'author': self.author.id,
            'tag_ids': [tag.id],
        }
        res = self.client.post(POSTS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.data['tags']), 1)
        self.assertEqual(res.data['tags'][0]['name'], 'flask')


class TestPostCategory(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_post_with_category(self):
        cat = Category.objects.create(name='Science')
        payload = {
            'title': 'Science Post',
            'content': 'Content',
            'author': self.author.id,
            'category': cat.id,
        }
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['category'], cat.id)
        self.assertEqual(res.data['category_name'], 'Science')

    def test_category_is_optional(self):
        payload = {'title': 'No Cat', 'content': 'Content', 'author': self.author.id}
        res = self.client.post(POSTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data['category'])


class TestPostSearch(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.client.force_authenticate(user=self.user)

    def test_search_posts_by_title(self):
        BlogPostModel.objects.create(
            title='Django Tips', content='Content', user=self.user, author=self.author,
        )
        BlogPostModel.objects.create(
            title='React Guide', content='Content', user=self.user, author=self.author,
        )
        res = self.client.get(POSTS_URL + '?search=django')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['title'], 'Django Tips')

    def test_filter_posts_by_status(self):
        BlogPostModel.objects.create(
            title='Draft', content='Content', user=self.user,
            author=self.author, status='draft',
        )
        BlogPostModel.objects.create(
            title='Published', content='Content', user=self.user,
            author=self.author, status='published',
        )
        res = self.client.get(POSTS_URL + '?status=draft')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['status'], 'draft')

    def test_ordering_by_created_at(self):
        BlogPostModel.objects.create(
            title='First', content='Content', user=self.user, author=self.author,
        )
        BlogPostModel.objects.create(
            title='Second', content='Content', user=self.user, author=self.author,
        )
        res = self.client.get(POSTS_URL + '?ordering=created_at')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in res.data['results']]
        self.assertEqual(titles[0], 'First')
