from django.contrib.auth import get_user_model
from .models import AuthorModel, BlogPostModel, Comment, Reaction, Notification, Citation, PostVersion
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


class PublicPostSerializer(serializers.ModelSerializer):
    author_handle = serializers.CharField(source='user.handle', read_only=True)
    reaction_count = serializers.IntegerField(source='reactions.count', read_only=True)

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'slug', 'content', 'author_handle',
            'status', 'visibility', 'published_at', 'created_at', 'reaction_count',
        ]


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

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'status', 'visibility', 'slug',
            'published_at', 'scheduled_for',
            'created_at', 'updated_at', 'image', 'user',
            'reason_for_change',
        ]
        read_only_fields = ['id', 'slug', 'published_at', 'created_at', 'updated_at', 'user']


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


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostModel
        fields = ['id', "image"]
        read_only_fields = ["id"]
