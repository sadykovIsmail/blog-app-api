from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    AuthorModel, BlogPostModel, Category, Tag,
    UserProfile, Comment, Like, Bookmark,
)
from .serializers import (
    AuthorSerializer, BlogPostSerializer, PostImageSerializer,
    CategorySerializer, TagSerializer, UserProfileSerializer,
    UserRegistrationSerializer, CommentSerializer, BookmarkSerializer,
)
from .filters import BlogPostFilter

User = get_user_model()


# ─── Permissions ──────────────────────────────────────────────────────────────

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_staff


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'detail': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


# ─── Profile ──────────────────────────────────────────────────────────────────

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# ─── Categories & Tags ────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


# ─── Authors ──────────────────────────────────────────────────────────────────

class AuthorViews(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = AuthorModel.objects.all()

    def get_queryset(self):
        return AuthorModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── Blog Posts (private — owner's posts only) ────────────────────────────────

class BlogPostViews(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    queryset = BlogPostModel.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlogPostFilter
    search_fields = ['title', 'content', 'author__name', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'reading_time', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            BlogPostModel.objects
            .filter(user=self.request.user)
            .prefetch_related('tags', 'likes', 'bookmarks', 'comments')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'upload_image':
            return PostImageSerializer
        return self.serializer_class

    @extend_schema(request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {'image': {'type': 'string', 'format': 'binary'}},
            'required': ['image'],
        }
    })
    @action(methods=['POST'], detail=True, url_path='upload-image', parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='publish')
    def publish(self, request, pk=None):
        post = self.get_object()
        post.status = BlogPostModel.STATUS_PUBLISHED
        post.save()
        return Response(BlogPostSerializer(post, context={'request': request}).data)

    @action(methods=['POST'], detail=True, url_path='unpublish')
    def unpublish(self, request, pk=None):
        post = self.get_object()
        post.status = BlogPostModel.STATUS_DRAFT
        post.save()
        return Response(BlogPostSerializer(post, context={'request': request}).data)

    @action(methods=['POST'], detail=True, url_path='like')
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'liked': False, 'likes_count': post.likes.count()})
        return Response({'liked': True, 'likes_count': post.likes.count()}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_path='bookmark')
    def bookmark(self, request, pk=None):
        post = self.get_object()
        bm, created = Bookmark.objects.get_or_create(post=post, user=request.user)
        if not created:
            bm.delete()
            return Response({'bookmarked': False})
        return Response({'bookmarked': True}, status=status.HTTP_201_CREATED)

    @action(methods=['GET', 'POST'], detail=True, url_path='comments')
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            qs = post.comments.filter(parent=None)
            serializer = CommentSerializer(qs, many=True, context={'request': request})
            return Response(serializer.data)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Public Posts (read-only, published only) ─────────────────────────────────

class PublicPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlogPostFilter
    search_fields = ['title', 'content', 'author__name', 'tags__name']
    ordering_fields = ['created_at', 'reading_time', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            BlogPostModel.objects
            .filter(status=BlogPostModel.STATUS_PUBLISHED)
            .prefetch_related('tags', 'likes', 'bookmarks', 'comments')
            .select_related('author', 'category', 'user')
        )

    @action(methods=['GET'], detail=True, url_path='comments', permission_classes=[AllowAny])
    def comments(self, request, slug=None):
        post = self.get_object()
        qs = post.comments.filter(parent=None)
        serializer = CommentSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='like', permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'liked': False, 'likes_count': post.likes.count()})
        return Response({'liked': True, 'likes_count': post.likes.count()}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_path='bookmark', permission_classes=[IsAuthenticated])
    def bookmark(self, request, slug=None):
        post = self.get_object()
        bm, created = Bookmark.objects.get_or_create(post=post, user=request.user)
        if not created:
            bm.delete()
            return Response({'bookmarked': False})
        return Response({'bookmarked': True}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_path='comments/add', permission_classes=[IsAuthenticated])
    def add_comment(self, request, slug=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Comments (edit/delete own) ───────────────────────────────────────────────

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── Bookmarks list ───────────────────────────────────────────────────────────

class BookmarkListView(generics.ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post')
