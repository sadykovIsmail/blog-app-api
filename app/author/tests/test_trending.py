from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel, Reaction

User = get_user_model()


def make_user(username='trenduser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_post(user, title='Trending Post', days_ago=0):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Some content here for trending',
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
    )
    if days_ago > 0:
        BlogPostModel.objects.filter(pk=post.pk).update(
            published_at=timezone.now() - timedelta(days=days_ago)
        )
        post.refresh_from_db()
    return post


class TrendingPostsTests(TestCase):
    def setUp(self):
        self.user = make_user(username='trenduser1')
        self.user2 = make_user(username='trenduser2')
        self.user3 = make_user(username='trenduser3')
        self.client = APIClient()

    def test_trending_endpoint_returns_200(self):
        response = self.client.get('/api/public/posts/trending/')
        self.assertEqual(response.status_code, 200)

    def test_post_with_more_reactions_ranks_higher(self):
        post_low = make_post(self.user, 'Low Reactions Post')
        post_high = make_post(self.user, 'High Reactions Post')
        # Give high post more reactions
        Reaction.objects.create(user=self.user2, post=post_high)
        Reaction.objects.create(user=self.user3, post=post_high)
        response = self.client.get('/api/public/posts/trending/')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        ids = [r['id'] for r in results]
        self.assertIn(post_high.id, ids)
        self.assertLess(ids.index(post_high.id), ids.index(post_low.id))

    def test_posts_older_than_30_days_excluded(self):
        old_post = make_post(self.user, 'Old Post', days_ago=31)
        recent_post = make_post(self.user, 'Recent Post', days_ago=1)
        response = self.client.get('/api/public/posts/trending/')
        self.assertEqual(response.status_code, 200)
        ids = [r['id'] for r in response.data['results']]
        self.assertNotIn(old_post.id, ids)
        self.assertIn(recent_post.id, ids)

    def test_returns_paginated_response(self):
        response = self.client.get('/api/public/posts/trending/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

    def test_post_with_more_comments_ranks_higher(self):
        from author.models import Comment
        post_low = make_post(self.user, 'Few Comments Post')
        post_high = make_post(self.user, 'Many Comments Post')
        Comment.objects.create(post=post_high, user=self.user2, body='Comment 1')
        Comment.objects.create(post=post_high, user=self.user3, body='Comment 2')
        response = self.client.get('/api/public/posts/trending/')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        ids = [r['id'] for r in results]
        self.assertIn(post_high.id, ids)
