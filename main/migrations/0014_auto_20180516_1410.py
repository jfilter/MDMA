# Generated by Django 2.0.5 on 2018-05-16 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20180516_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputimage',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='styleimage',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
