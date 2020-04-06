from .models import Group, PendingMembers
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'owner', 'members']
        read_only_fields = ['owner', 'id']


class PendingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingMembers
        fields = ['user']
