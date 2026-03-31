from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='reader', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_post(user, content, status=BlogPostModel.Status.PUBLISHED):
    author = AuthorModel.objects.create(name='Auth', email='a@a.com', user=user)
    post = BlogPostModel.objects.create(
        title='Test Post',
        content=content,
        author=author,
        user=user,
        status=status,
        visibility=BlogPostModel.Visibility.PUBLIC,
    )
    return post


class ReadingTimeSerializerTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_200_words_returns_1_minute(self):
        content = ' '.join(['word'] * 200)
        post = make_post(self.user, content)
        from author.serializers import PublicPostSerializer
        data = PublicPostSerializer(post).data
        self.assertEqual(data['reading_time_minutes'], 1)

    def test_400_words_returns_2_minutes(self):
        content = ' '.join(['word'] * 400)
        post = make_post(self.user, content)
        from author.serializers import PublicPostSerializer
        data = PublicPostSerializer(post).data
        self.assertEqual(data['reading_time_minutes'], 2)

    def test_50_words_returns_minimum_1_minute(self):
        content = ' '.join(['word'] * 50)
        post = make_post(self.user, content)
        from author.serializers import PublicPostSerializer
        data = PublicPostSerializer(post).data
        self.assertEqual(data['reading_time_minutes'], 1)

    def test_reading_time_in_public_feed(self):
        content = ' '.join(['word'] * 200)
        make_post(self.user, content)
        client = APIClient()
        response = client.get('/api/public/posts/')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertGreater(len(results), 0)
        self.assertIn('reading_time_minutes', results[0])

    def test_reading_time_in_my_posts(self):
        content = ' '.join(['word'] * 400)
        make_post(self.user, content)
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertGreater(len(results), 0)
        self.assertIn('reading_time_minutes', results[0])
