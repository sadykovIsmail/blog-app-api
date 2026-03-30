from django.contrib.auth import get_user_model
from .models import AuthorModel, BlogPostModel, Comment, Reaction, Notification, Citation, PostVersion, PostReview, Tag, Bookmark
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'handle']
        read_only_fields = ['id', 'handle']
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'handle']
        read_only_fields = ['id', 'username', 'email']

    def validate_handle(self, value):
        qs = User.objects.filter(handle=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This handle is already taken.")
        return value


class UserPublicProfileSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'handle', 'follower_count', 'following_count']

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']

    def validate_name(self, value):
        if Tag.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A tag with this name already exists.")
        return value


class PublicPostSerializer(serializers.ModelSerializer):
    author_handle = serializers.CharField(source='user.handle', read_only=True)
    reaction_count = serializers.IntegerField(source='reactions.count', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time_minutes = serializers.SerializerMethodField()

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'slug', 'content', 'author_handle',
            'status', 'visibility', 'published_at', 'created_at', 'reaction_count', 'tags',
            'reading_time_minutes',
        ]

    def get_reading_time_minutes(self, obj):
        return max(1, len(obj.content.split()) // 200)


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer"""
    user_name = serializers.CharField(
        source='user.username',
        read_only=True,
    )

    class Meta:
        model = AuthorModel
        fields = ['id', 'name', 'email', 'created_at', 'user', 'user_name']
        read_only_fields = ['id', 'created_at', 'user']


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    reason_for_change = serializers.CharField(write_only=True, required=False, allow_blank=True)
    reading_time_minutes = serializers.SerializerMethodField()

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'status', 'visibility', 'slug',
            'published_at', 'scheduled_for',
            'created_at', 'updated_at', 'image', 'user',
            'reason_for_change', 'reading_time_minutes',
        ]
        read_only_fields = ['id', 'slug', 'published_at', 'created_at', 'updated_at', 'user']

    def get_reading_time_minutes(self, obj):
        return max(1, len(obj.content.split()) // 200)

    def validate(self, data):
        import re
        status = data.get('status', getattr(self.instance, 'status', None))
        content = data.get('content', getattr(self.instance, 'content', ''))
        if status == BlogPostModel.Status.PUBLISHED:
            if not content or not content.strip():
                raise serializers.ValidationError(
                    {"content": "Content cannot be empty when publishing."}
                )
            links = re.findall(r'https?://\S+', content)
            if len(links) > 20:
                raise serializers.ValidationError(
                    {"content": "Published posts may not contain more than 20 external links."}
                )
        return data


class PostReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source='reviewer.username')

    class Meta:
        model = PostReview
        fields = ['id', 'post', 'reviewer', 'rating', 'notes', 'created_at']
        read_only_fields = ['id', 'post', 'reviewer', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class PostVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVersion
        fields = ['id', 'version_number', 'title_snapshot', 'content_snapshot',
                  'reason_for_change', 'changed_at']
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'parent', 'body', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'post', 'created_at', 'updated_at']


class CitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citation
        fields = [
            'id', 'post', 'url', 'title', 'publisher',
            'published_at', 'accessed_at',
            'http_status', 'checked_at', 'canonical_url', 'content_hash',
        ]
        read_only_fields = [
            'id', 'post', 'accessed_at', 'http_status',
            'checked_at', 'canonical_url', 'content_hash',
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'actor', 'post', 'comment', 'is_read', 'created_at']
        read_only_fields = fields


class BookmarkSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='post.title', read_only=True)
    slug = serializers.CharField(source='post.slug', read_only=True)
    post_id = serializers.IntegerField(source='post.id', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'post_id', 'title', 'slug', 'created_at']
        read_only_fields = fields


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostModel
        fields = ['id', "image"]
        read_only_fields = ["id"]
