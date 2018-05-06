from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class InputImage(models.Model):
    description = models.CharField(max_length=1024)
    copyright_notice = models.CharField(max_length=1024)
    image = models.FileField(upload_to='images/input')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class StyleImage(models.Model):
    description = models.CharField(max_length=1024)
    copyright_notice = models.CharField(max_length=1024)
    image = models.FileField(upload_to='images/style')
    uploaded_at = models.DateTimeField(auto_now_add=True)
