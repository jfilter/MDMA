import pathlib

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

import shortuuid

VISIBILITY_PRIVATE = 0
VISIBILITY_UNLISTED = 1
VISIBILITY_PUBLIC = 2

VISIBILITY_CHOICES = (
    (VISIBILITY_PUBLIC, 'public'),
    (VISIBILITY_UNLISTED, 'unlisted'),
    (VISIBILITY_PRIVATE, 'private'),
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


def random_file_path(prefix, filename):
    suffix = pathlib.Path(filename).suffix
    return prefix + shortuuid.ShortUUID().random(length=50) + suffix


def random_input_image_file_path(instance, filename):
    return random_file_path('static/images/input/', filename)


def random_output_image_file_path(instance, filename):
    return random_file_path('static/images/output/', filename)


class User(AbstractUser):
    pass


class InputImage(models.Model):
    def natural_key(self):
        return (self.image.url)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to=random_input_image_file_path, validators=[
        FileExtensionValidator(['jpg', 'png'])])
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    public_domain = models.BooleanField(default=False)
    copyright_notice = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    visibility = models.IntegerField(
        choices=VISIBILITY_CHOICES, default=VISIBILITY_CHOICES[0][0])


class StyleImage(models.Model):
    def natural_key(self):
        return (self.image.url)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    copyright_notice = models.TextField()
    image = models.ImageField(
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
    created_at = models.DateTimeField(auto_now_add=True)
    job_started_at = models.DateTimeField(null=True)
    job_finished_at = models.DateTimeField(null=True)
    style_weight = models.FloatField(null=True, default=1, validators=[
        MaxValueValidator(1),
        MinValueValidator(0)
    ])
    uuid = models.CharField(max_length=50, unique=True)
    output_image = models.ImageField(
        null=True, upload_to=random_output_image_file_path)
