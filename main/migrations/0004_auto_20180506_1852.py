# Generated by Django 2.0.5 on 2018-05-06 18:52

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20180506_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputimage',
            name='image',
            field=models.FileField(upload_to=main.models.random_input_image_file_path),
        ),
    ]
