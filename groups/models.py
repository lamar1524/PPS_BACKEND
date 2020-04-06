from django.db import models
from users.models import User


class Group(models.Model):
    name = models.CharField(max_length=127, null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wykladowca')
    members = models.ManyToManyField(User, related_name='students', blank=True)


class PendingMembers(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def is_pending(self, user, group):
        return user == self.user and group == self.group
