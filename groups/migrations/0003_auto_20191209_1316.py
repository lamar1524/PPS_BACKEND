# Generated by Django 2.2.6 on 2019-12-09 12:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20191209_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(null=True, related_name='students', to=settings.AUTH_USER_MODEL),
        ),
    ]
