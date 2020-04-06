from rest_framework import serializers

from posts.models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['owner', 'content', 'date_posted', 'group']
        read_only_fields = ['owner', 'group']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post', 'content', 'owner', 'date_commented']
        read_only_fields = ['owner', 'post']
