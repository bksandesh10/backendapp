from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils.timezone import now, timedelta


class AuthUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'   # login with email instead of username
    REQUIRED_FIELDS = ['username']


class UserProfile(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    DOB = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True , null=True)
    profile_pic = models.FileField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class TempUser(models.Model):
    temp_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=255)  # hashed password
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email