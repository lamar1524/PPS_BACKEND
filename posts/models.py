from django.db import models
from users.models import User
from groups.models import Group


def upload_location(instance, filename):
    return "%s/%s" %(instance.owner, filename)


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=1027)
    date_posted = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    file = models.FileField(blank=True, max_length=None, upload_to=upload_location)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=511)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_commented = models.DateTimeField(auto_now_add=True)
    file = models.FileField(blank=True, max_length=None, upload_to=upload_location)

