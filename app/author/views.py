from rest_framework import viewsets, status, generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from .models import AuthorModel, BlogPostModel, Follow, Comment, Reaction
from .serializers import (
    AuthorSerializer, BlogPostSerializer, PublicPostSerializer,
    PostImageSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserPublicProfileSerializer, CommentSerializer,
)
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        return self.request.user


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PublicPostListView(generics.ListAPIView):
    serializer_class = PublicPostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        return BlogPostModel.objects.filter(
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
        ).select_related('author', 'user')


class PublicProfilePostsView(generics.ListAPIView):
    serializer_class = PublicPostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        user = get_object_or_404(User, handle=self.kwargs['handle'])
        return BlogPostModel.objects.filter(
            user=user,
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
        ).select_related('author', 'user')


class UserPublicProfileView(generics.RetrieveAPIView):
    serializer_class = UserPublicProfileSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        return get_object_or_404(User, pk=self.kwargs['pk'])


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        target = get_object_or_404(User, pk=pk)
        if target == request.user:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        _, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            return Response({"detail": "Already following."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Followed."}, status=status.HTTP_201_CREATED)


class UnfollowView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        target = get_object_or_404(User, pk=pk)
        deleted, _ = Follow.objects.filter(follower=request.user, following=target).delete()
        if not deleted:
            return Response({"detail": "Not following."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['post_id'], parent__isnull=True,
        ).select_related('user')

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=self.kwargs['post_id'])
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return [IsAuthenticated(), IsCommentOwner()]
        return [IsAuthenticated()]


class PostReactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk)
        reaction, created = Reaction.objects.get_or_create(user=request.user, post=post)
        if not created:
            reaction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Reacted."}, status=status.HTTP_201_CREATED)


class CommentReactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        comment = get_object_or_404(Comment, pk=pk)
        reaction, created = Reaction.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            reaction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Reacted."}, status=status.HTTP_201_CREATED)


class IsCommentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class AuthorViews(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = AuthorModel.objects.all()

    def get_queryset(self):
        return AuthorModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BlogPostViews(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    queryset = BlogPostModel.objects.all()

    def get_queryset(self):
        # Only return posts of the logged-in user
        return BlogPostModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return PostImageSerializer
        return self.serializer_class

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "image": {"type": "string", "format": "binary"}
                },
                "required": ["image"],
            }
        }
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
