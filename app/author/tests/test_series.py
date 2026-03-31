from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='seriesuser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_post(user, title='Test Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'a{title}@a.com', user=user)
    return BlogPostModel.objects.create(
        title=title,
        content='Some content here',
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
    )


class SeriesTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.other_user = make_user(username='otheruser2')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_series_returns_201(self):
        response = self.client.post('/api/series/', {'title': 'My Series', 'description': 'A test series'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'My Series')

    def test_list_series_returns_200(self):
        self.client.post('/api/series/', {'title': 'Series One'})
        response = self.client.get('/api/series/')
        self.assertEqual(response.status_code, 200)

    def test_series_slug_auto_generated(self):
        response = self.client.post('/api/series/', {'title': 'Auto Slug Series'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('slug', response.data)
        self.assertEqual(response.data['slug'], 'auto-slug-series')

    def test_get_series_detail(self):
        create_resp = self.client.post('/api/series/', {'title': 'Detail Series'})
        series_id = create_resp.data['id']
        response = self.client.get(f'/api/series/{series_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Detail Series')

    def test_add_post_to_series(self):
        create_resp = self.client.post('/api/series/', {'title': 'Post Series'})
        series_id = create_resp.data['id']
        post = make_post(self.user)
        response = self.client.post(f'/api/series/{series_id}/posts/', {'post_id': post.id, 'order': 1})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['post_id'], post.id)

    def test_remove_post_from_series(self):
        create_resp = self.client.post('/api/series/', {'title': 'Remove Series'})
        series_id = create_resp.data['id']
        post = make_post(self.user)
        self.client.post(f'/api/series/{series_id}/posts/', {'post_id': post.id})
        response = self.client.delete(f'/api/series/{series_id}/posts/', {'post_id': post.id}, format='json')
        self.assertEqual(response.status_code, 204)

    def test_only_owner_can_add_posts(self):
        create_resp = self.client.post('/api/series/', {'title': 'Owner Series'})
        series_id = create_resp.data['id']
        post = make_post(self.user)
        other_client = APIClient()
        other_client.force_authenticate(user=self.other_user)
        response = other_client.post(f'/api/series/{series_id}/posts/', {'post_id': post.id})
        self.assertEqual(response.status_code, 404)
