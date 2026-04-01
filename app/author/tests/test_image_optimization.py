import io
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from author.models import AuthorModel, BlogPostModel
from PIL import Image as PILImage

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, email=f"{username}@x.com", password="pass")


def make_post(user):
    author = AuthorModel.objects.create(name="A", email="a@a.com", user=user)
    return BlogPostModel.objects.create(
        title="Image Post", content="content", author=author, user=user, status="DRAFT",
    )


def make_image(width=2000, height=1500, fmt="PNG"):
    buf = io.BytesIO()
    img = PILImage.new("RGB", (width, height), color=(255, 100, 50))
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


class ImageOptimizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user("imguser")
        self.client.force_authenticate(user=self.user)
        self.post = make_post(self.user)

    def test_upload_large_image_gets_resized(self):
        img_data = make_image(2000, 1500)
        upload = SimpleUploadedFile("big.png", img_data.read(), content_type="image/png")
        res = self.client.post(
            f"/api/posts/{self.post.id}/upload-image/",
            {"image": upload}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        if self.post.image:
            with PILImage.open(self.post.image) as img:
                self.assertLessEqual(img.width, 1200)

    def test_upload_small_image_not_upscaled(self):
        img_data = make_image(400, 300)
        upload = SimpleUploadedFile("small.png", img_data.read(), content_type="image/png")
        res = self.client.post(
            f"/api/posts/{self.post.id}/upload-image/",
            {"image": upload}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        if self.post.image:
            with PILImage.open(self.post.image) as img:
                self.assertLessEqual(img.width, 1200)

    def test_upload_returns_image_url(self):
        img_data = make_image(800, 600)
        upload = SimpleUploadedFile("test.png", img_data.read(), content_type="image/png")
        res = self.client.post(
            f"/api/posts/{self.post.id}/upload-image/",
            {"image": upload}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
