from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from author.models import AuthorModel, BlogPostModel, Comment

User = get_user_model()


def create_user(username='commenter', password='pass12345'):
    return User.objects.create_user(username=username, password=password)


def create_author(user):
    return AuthorModel.objects.create(user=user, name='Author', email='a@example.com')


def create_post(user, author, status_val='published'):
    return BlogPostModel.objects.create(
        title='Post', content='Content here', user=user,
        author=author, status=status_val,
    )


class TestComments(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)
        self.client.force_authenticate(user=self.user)

    def test_add_comment_to_own_post(self):
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.post(url, {'content': 'Great post!'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)

    def test_list_comments_on_own_post(self):
        Comment.objects.create(post=self.post, user=self.user, content='First comment')
        Comment.objects.create(post=self.post, user=self.user, content='Second comment')
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_reply_to_comment(self):
        parent = Comment.objects.create(post=self.post, user=self.user, content='Parent')
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.post(url, {'content': 'Reply', 'parent': parent.id})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(parent=parent).count(), 1)

    def test_replies_nested_in_parent(self):
        parent = Comment.objects.create(post=self.post, user=self.user, content='Parent')
        Comment.objects.create(post=self.post, user=self.user, content='Reply', parent=parent)
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        top_comments = res.data
        self.assertEqual(len(top_comments), 1)
        self.assertEqual(len(top_comments[0]['replies']), 1)

    def test_unauthenticated_cannot_comment(self):
        self.client.force_authenticate(user=None)
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.post(url, {'content': 'Sneaky'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_delete_own_comment(self):
        comment = Comment.objects.create(post=self.post, user=self.user, content='Delete me')
        url = reverse('comment-detail', args=[comment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_user_cannot_delete_others_comment(self):
        other_user = create_user('other', 'pass12345')
        comment = Comment.objects.create(post=self.post, user=other_user, content='Not mine')
        url = reverse('comment-detail', args=[comment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_comment_content_max_length(self):
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.post(url, {'content': 'x' * 1001})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_comment_fails(self):
        url = reverse('blogpostmodel-comments', args=[self.post.id])
        res = self.client.post(url, {'content': ''})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestPublicComments(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user('postowner', 'pass12345')
        self.author = create_author(self.user)
        self.post = create_post(self.user, self.author)

    def test_anyone_can_read_public_post_comments(self):
        Comment.objects.create(post=self.post, user=self.user, content='Public comment')
        url = reverse('public-post-comments', args=[self.post.slug])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_authenticated_user_can_add_comment_on_public_post(self):
        commenter = create_user('commenter2', 'pass12345')
        self.client.force_authenticate(user=commenter)
        url = reverse('public-post-add-comment', args=[self.post.slug])
        res = self.client.post(url, {'content': 'Nice post!'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
