from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    AuthorModel, BlogPostModel, Category, Tag,
    UserProfile, Comment, Like, Bookmark,
)

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'website', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_post_count(self, obj):
        return obj.posts.filter(status=BlogPostModel.STATUS_PUBLISHED).count()


class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_post_count(self, obj):
        return obj.posts.filter(status=BlogPostModel.STATUS_PUBLISHED).count()


class AuthorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuthorModel
        fields = ['id', 'name', 'email', 'created_at', 'user', 'user_name']
        read_only_fields = ['id', 'created_at', 'user']


class TagMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    tags = TagMinimalSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
        write_only=True, source='tags', required=False,
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'author_name',
            'category', 'category_name', 'tags', 'tag_ids',
            'status', 'reading_time', 'image',
            'likes_count', 'comments_count', 'is_liked', 'is_bookmarked',
            'created_at', 'updated_at', 'user',
        ]
        read_only_fields = ['id', 'slug', 'reading_time', 'created_at', 'updated_at', 'user']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.filter(parent=None).count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostModel
        fields = ['id', 'image']
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'username', 'parent',
            'content', 'replies', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.parent is None:
            qs = obj.replies.all()
            return CommentSerializer(qs, many=True, context=self.context).data
        return []


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class BookmarkSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_slug = serializers.CharField(source='post.slug', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'post', 'post_title', 'post_slug', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
