# Generated by Django 3.0.5 on 2020-05-03 12:08

from django.db import migrations, models
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20200420_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=posts.models.upload_location),
        ),
    ]