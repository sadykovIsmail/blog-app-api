from django.contrib.auth import get_user_model
from .models import AuthorModel, BlogPostModel
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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
    author_name = serializers.CharField(
        source='author.name',
        read_only=True,
    )

    class Meta:
        model = BlogPostModel
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostModel
        fields = ['id', "image"]
        read_only_fields = ["id"]
