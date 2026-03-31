from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from io import StringIO
from django.core.management import call_command
from author.models import AuthorModel, BlogPostModel

User = get_user_model()


def make_user(username='scheduser', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_post(user, title='Scheduled Post', status=BlogPostModel.Status.SCHEDULED, scheduled_for=None):
    author = AuthorModel.objects.create(name='Auth', email=f'{title.replace(" ", "")}@a.com', user=user)
    post = BlogPostModel.objects.create(
        title=title,
        content='Content for scheduled post test.',
        author=author,
        user=user,
        status=status,
        scheduled_for=scheduled_for,
    )
    return post


class ScheduledPublishingTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_past_scheduled_post_gets_published(self):
        """Post with scheduled_for in the past and status=SCHEDULED gets published."""
        past = timezone.now() - timedelta(hours=1)
        post = make_post(self.user, title='Past Scheduled', scheduled_for=past)
        out = StringIO()
        call_command('publish_scheduled', stdout=out)
        post.refresh_from_db()
        self.assertEqual(post.status, BlogPostModel.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)

    def test_future_scheduled_post_stays_scheduled(self):
        """Post with scheduled_for in the future stays SCHEDULED."""
        future = timezone.now() + timedelta(hours=1)
        post = make_post(self.user, title='Future Scheduled', scheduled_for=future)
        out = StringIO()
        call_command('publish_scheduled', stdout=out)
        post.refresh_from_db()
        self.assertEqual(post.status, BlogPostModel.Status.SCHEDULED)

    def test_draft_post_not_affected(self):
        """Post with status=DRAFT is not affected by the command."""
        post = make_post(self.user, title='Draft Post', status=BlogPostModel.Status.DRAFT, scheduled_for=None)
        out = StringIO()
        call_command('publish_scheduled', stdout=out)
        post.refresh_from_db()
        self.assertEqual(post.status, BlogPostModel.Status.DRAFT)

    def test_already_published_post_not_affected(self):
        """Already PUBLISHED posts are not affected."""
        past = timezone.now() - timedelta(hours=1)
        post = make_post(self.user, title='Already Published', status=BlogPostModel.Status.PUBLISHED, scheduled_for=past)
        original_published_at = post.published_at
        out = StringIO()
        call_command('publish_scheduled', stdout=out)
        post.refresh_from_db()
        self.assertEqual(post.status, BlogPostModel.Status.PUBLISHED)

    def test_command_outputs_correct_count(self):
        """Command outputs correct count message."""
        past = timezone.now() - timedelta(hours=1)
        make_post(self.user, title='Sched 1', scheduled_for=past)
        make_post(self.user, title='Sched 2', scheduled_for=past)
        out = StringIO()
        call_command('publish_scheduled', stdout=out)
        output = out.getvalue()
        self.assertIn('2', output)
        self.assertIn('Published', output)
