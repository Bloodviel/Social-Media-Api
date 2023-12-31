import os.path
import uuid

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "users", filename)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    username = models.CharField(max_length=60, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    bio = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to=user_image_file_path)
    followers = models.ManyToManyField(
        "User",
        default=0,
        related_name="follows",
        symmetrical=False
    )

    class Meta:
        ordering = ["first_name"]

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def followings_count(self):
        return self.follows.count()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
