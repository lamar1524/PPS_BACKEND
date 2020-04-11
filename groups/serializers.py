from users.serializers import UserSerializer
from .models import Group, PendingMembers
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'owner', 'members']
        read_only_fields = ['owner', 'id']


class PendingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingMembers
        fields = ['user']
