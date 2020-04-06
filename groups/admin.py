from django.contrib import admin
from .models import Group, PendingMembers
# Register your models here.
admin.site.register(Group)
admin.site.register(PendingMembers)