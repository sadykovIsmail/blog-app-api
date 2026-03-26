from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from author.models import AuthorModel, BlogPostModel, Like, Bookmark

User = get_user_model()

BOOKMARKS_URL = reverse('bookmarks')


def create_user(username='testuser', password='pass12345'):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name='Author', email='a@example.com')


def create_post(user, author, status_val='published'):
    return BlogPostModel.objects.create(
        title='Test Post', content='Content', user=user,
        author=author, status=status_val,
    )


class TestLikes(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.client.force_authenticate(user=self.user)

    def test_like_post(self):
        url = reverse('blogpostmodel-like', args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['liked'])
        self.assertEqual(Like.objects.filter(post=self.post).count(), 1)

    def test_unlike_post_toggle(self):
        Like.objects.create(post=self.post, user=self.user)
        url = reverse('blogpostmodel-like', args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['liked'])
        self.assertEqual(Like.objects.filter(post=self.post).count(), 0)

    def test_likes_count_in_post_serializer(self):
        Like.objects.create(post=self.post, user=self.user)
        other_user = create_user('other', 'pass12345')
        Like.objects.create(post=self.post, user=other_user)
        url = reverse('blogpostmodel-detail', args=[self.post.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['likes_count'], 2)

    def test_is_liked_field_reflects_user(self):
        url = reverse('blogpostmodel-detail', args=[self.post.id])
        res = self.client.get(url)
        self.assertFalse(res.data['is_liked'])

        Like.objects.create(post=self.post, user=self.user)
        res = self.client.get(url)
        self.assertTrue(res.data['is_liked'])

    def test_unauthenticated_cannot_like(self):
        self.client.force_authenticate(user=None)
        url = reverse('blogpostmodel-like', args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_public_post(self):
        other_user = create_user('other', 'pass12345')
        self.client.force_authenticate(user=other_user)
        url = reverse('public-post-like', args=[self.post.slug])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['liked'])


class TestBookmarks(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.client.force_authenticate(user=self.user)

    def test_bookmark_post(self):
        url = reverse('blogpostmodel-bookmark', args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['bookmarked'])
        self.assertEqual(Bookmark.objects.filter(post=self.post, user=self.user).count(), 1)

    def test_unbookmark_toggle(self):
        Bookmark.objects.create(post=self.post, user=self.user)
        url = reverse('blogpostmodel-bookmark', args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['bookmarked'])
        self.assertEqual(Bookmark.objects.filter(post=self.post, user=self.user).count(), 0)

    def test_is_bookmarked_field(self):
        url = reverse('blogpostmodel-detail', args=[self.post.id])
        res = self.client.get(url)
        self.assertFalse(res.data['is_bookmarked'])
        Bookmark.objects.create(post=self.post, user=self.user)
        res = self.client.get(url)
        self.assertTrue(res.data['is_bookmarked'])

    def test_bookmark_list_endpoint(self):
        other_user = create_user('other2', 'pass12345')
        other_author = create_author(other_user)
        other_post = create_post(other_user, other_author)
        Bookmark.objects.create(post=self.post, user=self.user)
        Bookmark.objects.create(post=other_post, user=other_user)
        res = self.client.get(BOOKMARKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_unauthenticated_cannot_bookmark(self):
        self.client.force_authenticate(user=None)
        url = reverse('blogpostmodel-bookmark', args=[self.post.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
