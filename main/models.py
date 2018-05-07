import pathlib

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

import shortuuid

VISIBILITY_PRIVATE = 0
VISIBILITY_UNLISTED = 1
VISIBILITY_PUBLIC = 2

VISIBILITY_CHOICES = (
    (VISIBILITY_PRIVATE, 'private'),
    (VISIBILITY_UNLISTED, 'unlisted'),
    (VISIBILITY_PUBLIC, 'public'),
)

STATUS_WATING = 0
STATUS_WORKING = 1
STATUS_FINISHED = 2
STATUS_FAILED = 3

STATUS_CHOICES = (
    (STATUS_WATING, 'waiting'),
    (STATUS_WORKING, 'working'),
    (STATUS_FINISHED, 'finished'),
    (STATUS_FAILED, 'failed')
)


def random_input_image_file_path(instance, filename):
    suffix = pathlib.Path(filename).suffix
    return 'static/images/input/' + shortuuid.ShortUUID().random(length=50) + suffix


class User(AbstractUser):
    pass


class InputImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    copyright_notice = models.TextField()
    image = models.FileField(upload_to=random_input_image_file_path, validators=[
                             FileExtensionValidator(['jpg', 'png'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    visibility = models.IntegerField(
        choices=VISIBILITY_CHOICES, default=VISIBILITY_CHOICES[0][0])


class StyleImage(models.Model):
    description = models.TextField()
    copyright_notice = models.TextField()
    image = models.FileField(
        upload_to='static/images/style', validators=[FileExtensionValidator(['jpg'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Job(models.Model):
    input_image = models.ForeignKey(
        InputImage, on_delete=models.CASCADE, null=True)
    style_image = models.ForeignKey(
        StyleImage, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    visibility = models.IntegerField(
        choices=VISIBILITY_CHOICES, default=VISIBILITY_CHOICES[0][0])
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_CHOICES[0][0])
    log = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    job_started_at = models.DateTimeField(null=True)
    job_finished_at = models.DateTimeField(null=True)
    num_steps = models.IntegerField(default=300, validators=[
        MaxValueValidator(500), MinValueValidator(10)])
    style_weight = models.IntegerField(default=1000)
    content_weight = models.IntegerField(default=1)
    uuid = models.CharField(max_length=50, blank=True, unique=True,
                            default=shortuuid.ShortUUID().random(length=50))
    output_image = models.FileField(null=True)
