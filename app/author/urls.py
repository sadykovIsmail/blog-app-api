from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import (
    AuthorViews, BlogPostViews, PublicPostViewSet,
    CategoryViewSet, TagViewSet, CommentViewSet,
    BookmarkListView,
)

router = DefaultRouter()
router.register('author', AuthorViews)
router.register('posts', BlogPostViews)
router.register('public/posts', PublicPostViewSet, basename='public-post')
router.register('categories', CategoryViewSet)
router.register('tags', TagViewSet)
router.register('comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bookmarks/', BookmarkListView.as_view(), name='bookmarks'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
