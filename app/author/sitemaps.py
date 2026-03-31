from django.contrib.sitemaps import Sitemap
from .models import BlogPostModel


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPostModel.objects.filter(
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/posts/{obj.slug}/"
