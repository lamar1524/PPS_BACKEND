from rest_framework import serializers

from groups.serializers import GroupSerializer
from posts.models import Post, Comment
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner')
    group = GroupSerializer(many=False, read_only=True)

    def to_representation(self, instance):
        to_return = super().to_representation(instance)
        to_return['group'] = {
            'id': to_return['group']['id'],
            'name': to_return['group']['name']
        }
        if to_return['image']:
            to_return['image'] = 'http://' + self.context['host'] + to_return['image']
        if to_return['file']:
            to_return['file'] = 'http://' + self.context['host'] + to_return['file']
        return to_return

    def get_owner(self, instance):
        return UserSerializer(instance=instance.owner, context=self.context).data

    class Meta:
        model = Post
        fields = ['id', 'owner', 'content', 'date_posted', 'group', 'file', 'image']
        read_only_fields = ['owner', 'group']


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'owner', 'date_commented', 'file']
        read_only_fields = ['owner', 'post']

    def get_owner(self, instance):
        return UserSerializer(instance=instance.owner, context=self.context).data

    def to_representation(self, instance):
        to_return = super().to_representation(instance)
        if to_return['file']:
            to_return['file'] = 'http://' + self.context['host'] + to_return['file']
        return to_return
