from rest_framework import viewsets, status, generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from .models import (
    AuthorModel, BlogPostModel, Follow, Comment,
    Reaction, Notification, Citation, PostVersion, PostReview,
    Report, ModerationAuditLog, Tag, Bookmark, Series, SeriesPost, Block, PostView,
)
from .serializers import (
    AuthorSerializer, BlogPostSerializer, PublicPostSerializer,
    PostImageSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserPublicProfileSerializer,
    CommentSerializer, NotificationSerializer, CitationSerializer,
    PostVersionSerializer, PostReviewSerializer, TagSerializer, BookmarkSerializer,
    SeriesSerializer,
)
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from .throttles import RegisterThrottle, CommentThrottle, FollowThrottle, EvidenceThrottle
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]


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
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
        qs = BlogPostModel.objects.filter(
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
        ).select_related('author', 'user').prefetch_related('reactions', 'tags')
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        search = self.request.query_params.get('search')
        if search:
            vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
            query = SearchQuery(search)
            qs = qs.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0.01).order_by('-rank')
        return qs

    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        from django.conf import settings as dj_settings
        if not request.query_params:
            cache_key = "public_feed_page_1"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            ttl = getattr(dj_settings, 'PUBLIC_FEED_CACHE_TTL', 30)
            cache.set(cache_key, response.data, ttl)
            return response
        return super().list(request, *args, **kwargs)


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
        ).select_related('author', 'user').prefetch_related('tags').order_by('-pinned', '-published_at')


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
    throttle_classes = [FollowThrottle]

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
        Notification.objects.create(
            recipient=target, actor=request.user, notification_type="follow",
        )
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
    throttle_classes = [CommentThrottle]

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['post_id'], parent__isnull=True,
        ).select_related('user')

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=self.kwargs['post_id'])
        comment = serializer.save(user=self.request.user, post=post)
        if comment.parent:
            if comment.parent.user != self.request.user:
                Notification.objects.create(
                    recipient=comment.parent.user, actor=self.request.user,
                    notification_type="reply", comment=comment,
                )
        elif post.user != self.request.user:
            Notification.objects.create(
                recipient=post.user, actor=self.request.user,
                notification_type="comment", post=post, comment=comment,
            )


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


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        unread_count = qs.filter(is_read=False).count()
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data['unread_count'] = unread_count
        return response


class PostReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = PostReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PostReview.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=self.kwargs['post_id'])
        if post.user == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You cannot review your own post.")
        serializer.save(reviewer=self.request.user, post=post)


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class ReportPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk)
        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response({"detail": "Reason is required."}, status=status.HTTP_400_BAD_REQUEST)
        Report.objects.create(
            reporter=request.user, target_type='post', post=post, reason=reason,
        )
        return Response({"detail": "Report submitted."}, status=status.HTTP_201_CREATED)


class ReportCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        comment = get_object_or_404(Comment, pk=pk)
        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response({"detail": "Reason is required."}, status=status.HTTP_400_BAD_REQUEST)
        Report.objects.create(
            reporter=request.user, target_type='comment', comment=comment, reason=reason,
        )
        return Response({"detail": "Report submitted."}, status=status.HTTP_201_CREATED)


class HideCommentView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_hidden = True
        comment.save(update_fields=['is_hidden'])
        ModerationAuditLog.objects.create(
            actor=request.user,
            action='hide_comment',
            target_type='comment',
            target_id=comment.id,
        )
        return Response({"detail": "Comment hidden."}, status=status.HTTP_200_OK)


class PostChangelogView(generics.ListAPIView):
    serializer_class = PostVersionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=self.kwargs['pk'])
        return PostVersion.objects.filter(post=post)


class EvidencePanelView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [EvidenceThrottle]

    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk)
        citations = Citation.objects.filter(post=post)
        serializer = CitationSerializer(citations, many=True)
        return Response({
            "post_id": post.id,
            "citations": serializer.data,
        })


class IsPostOwner(BasePermission):
    def has_permission(self, request, view):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=view.kwargs.get('post_id'))
        return post.user == request.user


class CitationListCreateView(generics.ListCreateAPIView):
    serializer_class = CitationSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsPostOwner()]

    def get_queryset(self):
        return Citation.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=self.kwargs['post_id'])
        serializer.save(post=post)


class CitationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CitationSerializer
    queryset = Citation.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return [IsAuthenticated(), IsCitationOwner()]
        return [IsAuthenticated()]


class IsCitationOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.post.user == request.user


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
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        post = self.get_object()
        reason = serializer.validated_data.pop('reason_for_change', '')
        next_version = post.versions.count() + 1
        PostVersion.objects.create(
            post=post,
            version_number=next_version,
            title_snapshot=post.title,
            content_snapshot=post.content,
            reason_for_change=reason,
        )
        serializer.save()

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


class TagListCreateView(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class PostTagView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=post_id, user=request.user)
        tag_id = request.data.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        post.tags.add(tag)
        return Response(TagSerializer(tag).data)

    def delete(self, request, post_id, tag_id):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=post_id, user=request.user)
        tag = get_object_or_404(Tag, pk=tag_id)
        post.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk)
        obj, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response(BookmarkSerializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(BookmarkSerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk)
        bookmark = Bookmark.objects.filter(user=request.user, post=post).first()
        if not bookmark:
            return Response(status=status.HTTP_404_NOT_FOUND)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookmarkListView(generics.ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post').order_by('-created_at')


class IsSeriesOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class SeriesListCreateView(generics.ListCreateAPIView):
    serializer_class = SeriesSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Series.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SeriesDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SeriesSerializer
    queryset = Series.objects.all()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsSeriesOwner()]
        return [AllowAny()]


class SeriesPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, series_id):
        from django.shortcuts import get_object_or_404
        series = get_object_or_404(Series, pk=series_id, owner=request.user)
        post_id = request.data.get('post_id')
        order = request.data.get('order', 0)
        post = get_object_or_404(BlogPostModel, pk=post_id, user=request.user)
        obj, _ = SeriesPost.objects.get_or_create(series=series, post=post, defaults={'order': order})
        return Response({'series_id': series.id, 'post_id': post.id, 'order': obj.order}, status=201)

    def delete(self, request, series_id):
        from django.shortcuts import get_object_or_404
        series = get_object_or_404(Series, pk=series_id, owner=request.user)
        post_id = request.data.get('post_id')
        SeriesPost.objects.filter(series=series, post_id=post_id).delete()
        return Response(status=204)


class TrendingPostsView(generics.ListAPIView):
    serializer_class = PublicPostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=30)
        return BlogPostModel.objects.filter(
            status=BlogPostModel.Status.PUBLISHED,
            visibility=BlogPostModel.Visibility.PUBLIC,
            published_at__gte=cutoff,
        ).annotate(
            reaction_cnt=Count('reactions', distinct=True),
            comment_cnt=Count('comments', distinct=True),
        ).order_by('-reaction_cnt', '-comment_cnt', '-published_at').select_related('author', 'user').prefetch_related('reactions', 'tags')


class PostPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk, user=request.user)
        BlogPostModel.objects.filter(user=request.user, pinned=True).update(pinned=False)
        post.pinned = True
        post.save(update_fields=['pinned'])
        return Response({'pinned': True})

    def delete(self, request, pk):
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk, user=request.user)
        post.pinned = False
        post.save(update_fields=['pinned'])
        return Response({'pinned': False})


class BlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        target = get_object_or_404(User, pk=pk)
        if target == request.user:
            return Response({'detail': 'Cannot block yourself.'}, status=400)
        Block.objects.get_or_create(blocker=request.user, blocked=target)
        return Response({'detail': 'Blocked.'}, status=201)

    def delete(self, request, pk):
        Block.objects.filter(blocker=request.user, blocked_id=pk).delete()
        return Response(status=204)


class PostViewCountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        import hashlib
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(BlogPostModel, pk=pk, status=BlogPostModel.Status.PUBLISHED)
        ip = request.META.get('REMOTE_ADDR', '')
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        PostView.objects.get_or_create(post=post, ip_hash=ip_hash)
        return Response({'view_count': post.view_count})
