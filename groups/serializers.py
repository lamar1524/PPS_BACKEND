from posts.models import Post
from users.serializers import UserSerializer
from .models import Group, PendingMembers
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner')
    members = serializers.SerializerMethodField('get_members')

    class Meta:
        model = Group
        fields = ['id', 'name', 'owner', 'members']
        read_only_fields = ['owner', 'id']

    def get_owner(self, instance):
        return UserSerializer(instance=instance.owner, context=self.context).data

    def get_members(self, instance):
        return UserSerializer(instance.members, context=self.context, many=True).data


class PendingMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = PendingMembers
        fields = ['user']

    def get_user(self, instance):
        return UserSerializer(instance=instance.user, context=self.context).data
