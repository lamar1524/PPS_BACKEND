# Generated by Django 3.0.5 on 2020-05-06 11:47

from django.db import migrations, models
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_remove_post_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='file',
            field=models.FileField(blank=True, upload_to=posts.models.upload_location),
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to=posts.models.upload_location),
        ),
    ]
