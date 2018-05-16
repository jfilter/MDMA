from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class ImageStorage(S3Boto3Storage):
    if settings.DEBUG:
        location = 'images-development'
    else:
        location = 'images'
    file_overwrite = True
