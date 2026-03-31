from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import BlogPostModel


class LatestPostsFeed(Feed):
    title = "BlogApp — Latest Posts"
    link = "/api/public/posts/"
    description = "Latest published posts."

    def items(self):
        return BlogPostModel.objects.filter(
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
        ).order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:500]

    def item_link(self, item):
        return f"/api/public/posts/?slug={item.slug}"

    def item_pubdate(self, item):
        return item.published_at


class AuthorPostsFeed(Feed):
    feed_type = Atom1Feed

    def get_object(self, request, handle):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        return get_object_or_404(User, handle=handle)

    def title(self, user):
        return f"{user.handle}'s posts"

    def link(self, user):
        return f"/api/public/profiles/{user.handle}/posts/"

    def description(self, user):
        return f"Latest posts by {user.handle}"

    def items(self, user):
        return BlogPostModel.objects.filter(
            user=user,
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
        ).order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:500]

    def item_link(self, item):
        return f"/api/public/posts/?slug={item.slug}"

    def item_pubdate(self, item):
        return item.published_at
