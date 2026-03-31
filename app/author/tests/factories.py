"""
factory_boy factories for the author app.

Usage in tests:
    from author.tests.factories import UserFactory, BlogPostFactory

    user = UserFactory()
    post = BlogPostFactory(user=user)
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    handle = factory.LazyAttribute(lambda obj: obj.username)


class AuthorModelFactory(DjangoModelFactory):
    class Meta:
        model = "author.AuthorModel"

    name = factory.Faker("name")
    email = factory.Faker("email")
    user = factory.SubFactory(UserFactory)


class TagFactory(DjangoModelFactory):
    class Meta:
        model = "author.Tag"
        django_get_or_create = ("slug",)

    name = factory.Sequence(lambda n: f"tag-{n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class BlogPostFactory(DjangoModelFactory):
    class Meta:
        model = "author.BlogPostModel"

    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("text", max_nb_chars=500)
    author = factory.SubFactory(AuthorModelFactory, user=factory.SelfAttribute("..user"))
    user = factory.SubFactory(UserFactory)
    status = "DRAFT"
    visibility = "PUBLIC"


class PublishedPostFactory(BlogPostFactory):
    status = "PUBLISHED"

    @factory.lazy_attribute
    def published_at(self):
        from django.utils import timezone
        return timezone.now()


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = "author.Comment"

    post = factory.SubFactory(BlogPostFactory)
    user = factory.SubFactory(UserFactory)
    body = factory.Faker("sentence", nb_words=12)


class CitationFactory(DjangoModelFactory):
    class Meta:
        model = "author.Citation"

    post = factory.SubFactory(BlogPostFactory)
    url = factory.Sequence(lambda n: f"https://example.com/source/{n}")
    title = factory.Faker("sentence", nb_words=5)


class BookmarkFactory(DjangoModelFactory):
    class Meta:
        model = "author.Bookmark"

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(BlogPostFactory)


class FollowFactory(DjangoModelFactory):
    class Meta:
        model = "author.Follow"

    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = "author.Notification"

    recipient = factory.SubFactory(UserFactory)
    actor = factory.SubFactory(UserFactory)
    notification_type = "follow"


class SeriesFactory(DjangoModelFactory):
    class Meta:
        model = "author.Series"

    title = factory.Faker("sentence", nb_words=4)
    owner = factory.SubFactory(UserFactory)
