# Generated by Django 2.2.6 on 2019-12-09 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_date_joined'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='student',
        ),
        migrations.AlterField(
            model_name='user',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
