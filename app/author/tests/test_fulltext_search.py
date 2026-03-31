from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='searchuser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_post(user, title='Test Post', content='Default content'):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}search@a.com', user=user)
    return BlogPostModel.objects.create(
        title=title,
        content=content,
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
    )


class FullTextSearchTests(TestCase):
    def setUp(self):
        self.user = make_user(username='searchuser1')
        self.client = APIClient()

    def test_search_word_in_title_returns_matching_posts(self):
        make_post(self.user, 'Django REST Framework Guide', 'Learn about APIs')
        make_post(self.user, 'Python Tips', 'Python programming tips')
        response = self.client.get('/api/public/posts/?search=Django')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        titles = [r['title'] for r in results]
        self.assertIn('Django REST Framework Guide', titles)

    def test_search_is_case_insensitive(self):
        make_post(self.user, 'Django REST Framework Guide', 'Learn about APIs')
        response = self.client.get('/api/public/posts/?search=django')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        titles = [r['title'] for r in results]
        self.assertIn('Django REST Framework Guide', titles)

    def test_non_matching_search_returns_empty(self):
        make_post(self.user, 'Django REST Framework Guide', 'Learn about APIs')
        response = self.client.get('/api/public/posts/?search=xyznonexistentterm')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_endpoint_works_without_search_param(self):
        make_post(self.user, 'Some Post', 'Some content')
        response = self.client.get('/api/public/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)

    def test_search_in_content_returns_matching_posts(self):
        make_post(self.user, 'General Post', 'This post is about microservices architecture')
        make_post(self.user, 'Another Post', 'This post is about monoliths')
        response = self.client.get('/api/public/posts/?search=microservices')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        titles = [r['title'] for r in results]
        self.assertIn('General Post', titles)
