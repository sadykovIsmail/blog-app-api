from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='coauthoruser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_published_post(user, title='CoAuthor Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Content for co-author test post.',
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
        published_at=timezone.now(),
    )
    return post


class CoAuthorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = make_user(username='owner')
        self.other = make_user(username='coauthor2')
        self.post = make_published_post(self.owner)

    def test_add_coauthor_returns_201(self):
        """Add co-author returns 201."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/posts/{self.post.pk}/co-authors/',
            {'user_id': self.other.pk},
        )
        self.assertEqual(response.status_code, 201)

    def test_remove_coauthor_returns_204(self):
        """Remove co-author returns 204."""
        from author.models import CoAuthor
        CoAuthor.objects.create(post=self.post, user=self.other)
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(
            f'/api/posts/{self.post.pk}/co-authors/',
            {'user_id': self.other.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 204)

    def test_self_coauthor_returns_400(self):
        """Self-co-author returns 400."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/posts/{self.post.pk}/co-authors/',
            {'user_id': self.owner.pk},
        )
        self.assertEqual(response.status_code, 400)

    def test_only_post_owner_can_add_coauthor(self):
        """Only post owner can add co-authors."""
        self.client.force_authenticate(user=self.other)
        third = make_user(username='third')
        response = self.client.post(
            f'/api/posts/{self.post.pk}/co-authors/',
            {'user_id': third.pk},
        )
        self.assertEqual(response.status_code, 404)

    def test_coauthor_handles_in_public_feed(self):
        """co_author_handles appears in public feed."""
        from author.models import CoAuthor
        CoAuthor.objects.create(post=self.post, user=self.other)
        response = self.client.get('/api/public/posts/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', [])
        self.assertTrue(len(results) > 0)
        self.assertIn('co_author_handles', results[0])
