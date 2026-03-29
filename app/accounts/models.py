from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    handle = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Public profile handle, defaults to username.",
    )

    def save(self, *args, **kwargs):
        if not self.handle:
            self.handle = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.handle or self.username
