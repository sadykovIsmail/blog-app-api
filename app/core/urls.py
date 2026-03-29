"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from author.views import (
    RegisterView, ProfileView, PublicPostListView, PublicProfilePostsView,
    FollowView, UnfollowView, UserPublicProfileView,
    PostCommentListCreateView, CommentDetailView,
    PostReactView, CommentReactView, NotificationListView,
    CitationListCreateView, CitationDetailView, EvidencePanelView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('author.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    path('api/public/posts/', PublicPostListView.as_view(), name='public-post-list'),
    path('api/public/profiles/<str:handle>/posts/', PublicProfilePostsView.as_view(), name='public-profile-posts'),
    path('api/users/<int:pk>/', UserPublicProfileView.as_view(), name='profile-detail'),
    path('api/users/<int:pk>/follow/', FollowView.as_view(), name='follow'),
    path('api/users/<int:pk>/unfollow/', UnfollowView.as_view(), name='unfollow'),
    path('api/posts/<int:post_id>/comments/', PostCommentListCreateView.as_view(), name='post-comments'),
    path('api/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('api/posts/<int:pk>/react/', PostReactView.as_view(), name='post-react'),
    path('api/comments/<int:pk>/react/', CommentReactView.as_view(), name='comment-react'),
    path('api/notifications/', NotificationListView.as_view(), name='notifications'),
    path('api/posts/<int:post_id>/citations/', CitationListCreateView.as_view(), name='post-citations'),
    path('api/citations/<int:pk>/', CitationDetailView.as_view(), name='citation-detail'),
    path('api/posts/<int:pk>/evidence/', EvidencePanelView.as_view(), name='post-evidence'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
