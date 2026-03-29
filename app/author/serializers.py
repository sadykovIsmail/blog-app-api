from django.contrib.auth import get_user_model
from .models import AuthorModel, BlogPostModel
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

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'slug', 'content', 'author_handle',
            'status', 'visibility', 'published_at', 'created_at',
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

    class Meta:
        model = BlogPostModel
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'status', 'visibility', 'slug',
            'published_at', 'scheduled_for',
            'created_at', 'updated_at', 'image', 'user',
        ]
        read_only_fields = ['id', 'slug', 'published_at', 'created_at', 'updated_at', 'user']


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostModel
        fields = ['id', "image"]
        read_only_fields = ["id"]
