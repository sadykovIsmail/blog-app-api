from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='pinuser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com', handle=f'@{username}')


def make_post(user, title='Test Post'):
    author = AuthorModel.objects.create(name='Auth', email=f'{title}pin@a.com', user=user)
    return BlogPostModel.objects.create(
        title=title,
        content='Some content here',
        author=author,
        user=user,
        status=BlogPostModel.Status.PUBLISHED,
        visibility=BlogPostModel.Visibility.PUBLIC,
    )


class PinningTests(TestCase):
    def setUp(self):
        self.user = make_user(username='pinuser1')
        self.other_user = make_user(username='otheruserpin')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_pin_post_returns_200_with_pinned_true(self):
        post = make_post(self.user)
        response = self.client.post(f'/api/posts/{post.pk}/pin/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['pinned'])

    def test_unpin_post_returns_200_with_pinned_false(self):
        post = make_post(self.user)
        self.client.post(f'/api/posts/{post.pk}/pin/')
        response = self.client.delete(f'/api/posts/{post.pk}/pin/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['pinned'])

    def test_pinning_second_post_unpins_first(self):
        post1 = make_post(self.user, 'Post One')
        post2 = make_post(self.user, 'Post Two')
        self.client.post(f'/api/posts/{post1.pk}/pin/')
        self.client.post(f'/api/posts/{post2.pk}/pin/')
        post1.refresh_from_db()
        post2.refresh_from_db()
        self.assertFalse(post1.pinned)
        self.assertTrue(post2.pinned)

    def test_only_post_owner_can_pin(self):
        post = make_post(self.user)
        other_client = APIClient()
        other_client.force_authenticate(user=self.other_user)
        response = other_client.post(f'/api/posts/{post.pk}/pin/')
        self.assertEqual(response.status_code, 404)

    def test_pinned_posts_appear_first_in_profile(self):
        post1 = make_post(self.user, 'Older Post')
        post2 = make_post(self.user, 'Newer Post')
        # Pin the older post
        self.client.post(f'/api/posts/{post1.pk}/pin/')
        anon_client = APIClient()
        response = anon_client.get(f'/api/public/profiles/@pinuser1/posts/')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertGreater(len(results), 0)
        # The pinned post should appear first
        self.assertEqual(results[0]['id'], post1.id)
