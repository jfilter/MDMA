import pathlib

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

import shortuuid


def random_input_image_file_path(instance, filename):
    suffix = pathlib.Path(filename).suffix
    return 'static/images/input/' + shortuuid.ShortUUID().random(length=30) + suffix


class User(AbstractUser):
    pass


class InputImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=1024)
    copyright_notice = models.CharField(max_length=1024)
    image = models.FileField(upload_to=random_input_image_file_path, validators=[
                             FileExtensionValidator(['jpg', 'png'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)


class StyleImage(models.Model):
    description = models.CharField(max_length=1024)
    copyright_notice = models.CharField(max_length=1024)
    image = models.FileField(
        upload_to='static/images/style', validators=[FileExtensionValidator(['jpg'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
