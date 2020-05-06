from rest_framework import serializers

from groups.serializers import GroupSerializer
from posts.models import Post, Comment
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
    group = GroupSerializer(many=False, read_only=True)

    def to_representation(self, instance):
        to_return = super().to_representation(instance)
        to_return['group'] = {
            'id': to_return['group']['id'],
            'name': to_return['group']['name']
        }
        return to_return

    class Meta:
        model = Post
        fields = ['id', 'owner', 'content', 'date_posted', 'group', 'file', 'image']
        read_only_fields = ['owner', 'group']


class CommentSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'owner', 'date_commented', 'file']
        read_only_fields = ['owner', 'post']
