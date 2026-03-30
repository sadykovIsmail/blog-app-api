from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks',
    )
    post = models.ForeignKey(
        'BlogPostModel', on_delete=models.CASCADE, related_name='bookmarks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} bookmarked {self.post}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} -> {self.following}"


class Report(models.Model):
    class TargetType(models.TextChoices):
        POST = "post", "Post"
        COMMENT = "comment", "Comment"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_filed',
    )
    target_type = models.CharField(max_length=10, choices=TargetType.choices)
    post = models.ForeignKey(
        'BlogPostModel', null=True, blank=True, on_delete=models.CASCADE, related_name='reports',
    )
    comment = models.ForeignKey(
        'Comment', null=True, blank=True, on_delete=models.CASCADE, related_name='reports',
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} on {self.target_type}"


class ModerationAuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='moderation_actions',
    )
    action = models.CharField(max_length=50)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} — {self.action} at {self.created_at}"


class PostReview(models.Model):
    post = models.ForeignKey(
        'BlogPostModel', on_delete=models.CASCADE, related_name='reviews',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given',
    )
    rating = models.PositiveSmallIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'reviewer')

    def __str__(self):
        return f"Review by {self.reviewer} on {self.post} ({self.rating}/5)"


class PostVersion(models.Model):
    post = models.ForeignKey(
        'BlogPostModel', on_delete=models.CASCADE, related_name='versions',
    )
    version_number = models.PositiveIntegerField()
    title_snapshot = models.CharField(max_length=255)
    content_snapshot = models.TextField()
    reason_for_change = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['version_number']
        unique_together = ('post', 'version_number')

    def __str__(self):
        return f"{self.post} v{self.version_number}"


class Citation(models.Model):
    post = models.ForeignKey(
        'BlogPostModel', on_delete=models.CASCADE, related_name='citations',
    )
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    published_at = models.DateField(null=True, blank=True)
    accessed_at = models.DateField(auto_now_add=True)
    http_status = models.IntegerField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    canonical_url = models.URLField(max_length=2000, blank=True)
    content_hash = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"{self.url} ({self.post})"


class Notification(models.Model):
    class Type(models.TextChoices):
        FOLLOW = "follow", "Follow"
        COMMENT = "comment", "Comment"
        REPLY = "reply", "Reply"
        NEW_POST = "new_post", "New Post"
        CITATION_DEAD = "citation_dead", "Citation Dead"
        CITATION_DRIFT = "citation_drift", "Citation Drift"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',
    )
    notification_type = models.CharField(max_length=20, choices=Type.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sent_notifications',
    )
    post = models.ForeignKey(
        'BlogPostModel', null=True, blank=True, on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        'Comment', null=True, blank=True, on_delete=models.CASCADE,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.recipient}"


class Reaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions',
    )
    post = models.ForeignKey(
        'BlogPostModel', null=True, blank=True,
        on_delete=models.CASCADE, related_name='reactions',
    )
    comment = models.ForeignKey(
        'Comment', null=True, blank=True,
        on_delete=models.CASCADE, related_name='reactions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'post'), ('user', 'comment')]

    def __str__(self):
        target = f"post:{self.post_id}" if self.post_id else f"comment:{self.comment_id}"
        return f"{self.user} reacted to {target}"


class Comment(models.Model):
    post = models.ForeignKey(
        'BlogPostModel', on_delete=models.CASCADE, related_name='comments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments',
    )
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies',
    )
    body = models.TextField()
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"


class AuthorModel(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BlogPostModel(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SCHEDULED = "SCHEDULED", "Scheduled"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(max_length=200)
    content = models.TextField(max_length=50000)
    author = models.ForeignKey(AuthorModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True, upload_to="posts/")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="posts",
    )
    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        UNLISTED = "UNLISTED", "Unlisted"

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    class Meta:
        indexes = [
            models.Index(fields=['status', 'visibility']),
            models.Index(fields=['-published_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        if self.status == self.Status.PUBLISHED and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base = slugify(self.title)
        slug = base
        n = 1
        while BlogPostModel.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def __str__(self):
        return self.title
