from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .managers import CustomUserManager
import pytz


class User(AbstractUser):
    name = models.CharField(max_length=25)
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    password = models.CharField(max_length=128)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "password"]
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class RefferalSystem(models.Model):
    code = models.CharField(max_length=20, unique=True, editable=False)
    isActive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=False)

    refer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='referrals_received')

    referal = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='referrals_given', null=True, default=None
    )

    def __str__(self):
        return self.code
