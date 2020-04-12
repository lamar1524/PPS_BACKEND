from datetime import datetime
from operator import itemgetter, attrgetter

from django.http import JsonResponse
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination
from groups.models import Group
from posts.models import Post, Comment
from posts.permissions import IsObjOwner, IsGroupMember, IsGroupOrPostOwner, IsGroupOrPostOrCommentOwner
from posts.serializers import PostSerializer, CommentSerializer
from django.db.models.query import QuerySet


class PostViewSet(viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # KAŻDY CZŁONEK GRUPY
    @action(methods=['post'], detail=False, url_name='create', url_path=r'create/(?P<group_id>\d+)')
    def create_post(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('group_id'))
        self.check_object_permissions(request, group)
        serializer = PostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer.save(owner=request.user, group=group)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    # WŁAŚCICIEL POSTA
    @action(methods=['delete'], detail=False, url_name='delete', url_path=r'delete/(?P<post_id>\d+)')
    def delete_post(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs.get('post_id'))
        self.check_object_permissions(request, post)
        post.delete()
        return Response(data={'message': 'Pomyślnie usunięto'})

    @action(methods=['put'], detail=False, url_name='edit', url_path=r'edit/(?P<post_id>\d+)')
    def edit_post(self, request, **kwargs):
        post = Post.objects.get(id=kwargs.get('post_id'))
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, request.data, partial=True)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer.update(post, serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # każdy członek grupy
    @action(methods=['get'], detail=False, url_name='posts', url_path=r'group/(?P<group_id>\d+)')
    def posts_list(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('group_id'))
        self.check_object_permissions(request, group)
        try:
            posts = Post.objects.filter(group=group).order_by('-date_posted')
        except Post.DoesNotExist():
            return Response(data={'message': 'Posts in this group were not found'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        users_posts = PostSerializer(posts, many=True).data
        paginator = PageNumberPagination()
        data = paginator.paginate_queryset(users_posts, request)
        return paginator.get_paginated_response(data=data)

    # każdy user z wszystkich jego grup
    @action(methods=['post'], detail=False, url_name='my_posts', url_path='my_posts')
    def users_groups_posts_list(self, request):
        users_groups = Group.objects.filter(members=request.user) | Group.objects.filter(owner=request.user)
        if len(users_groups) == 0:
            return Response(data={'message': 'Your groups were not found'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        groups_posts = QuerySet(Post)
        for group in users_groups:
            groups_posts = groups_posts | Post.objects.filter(group=group)
        groups_posts = sorted(groups_posts, key=attrgetter('date_posted'), reverse=True)
        if len(groups_posts) == 0:
            return Response(data={'message': 'Your posts were not found'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        users_posts = PostSerializer(groups_posts, many=True).data
        paginator = PageNumberPagination()
        data = paginator.paginate_queryset(users_posts, request)
        return paginator.get_paginated_response(data=data)

    @action(methods=['get'], detail=False, url_name='detail', url_path=r'post/(?P<post_id>\d+)')
    def post_detail(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs.get('post_id'))
        self.check_object_permissions(request, post.group)
        response_data = {
            'post': PostSerializer(post).data,
            'comments': CommentSerializer(Comment.objects.filter(post=post)).data
        }
        return JsonResponse(data=response_data, status=200, safe=False)

    @action(methods=['delete'], detail=False, url_name='comment_delete',
            url_path=r'post/(?P<post_id>\d+)/comment/(?P<comment_id>\d+)/delete')
    def comment_delete(self, request, **kwargs):
        post = get_object_or_404(Post, id=kwargs.get('post_id'))
        comment = get_object_or_404(Comment, id=kwargs.get('comment_id'), post=post)
        self.check_object_permissions(request, comment)
        comment.delete()
        return JsonResponse(data={'message': 'Pomyślnie usunięto komentarz'}, status=200, safe=False)

    @action(methods=['put'], detail=False, url_name='comment_edit',
            url_path=r'post/(?P<post_id>\d+)/comment/(?P<comment_id>\d+)/edit')
    def comment_edit(self, request, **kwargs):
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        post = get_object_or_404(Post, id=kwargs.get('post_id'))
        comment = get_object_or_404(Comment, id=kwargs.get('comment_id'), post=post)
        self.check_object_permissions(request, comment)
        serializer.update(comment, serializer.validated_data)
        return JsonResponse(data=serializer.data, status=200, safe=False)

    @action(methods=['post'], detail=False, url_name='comment_add',
            url_path=r'post/(?P<post_id>\d+)/comment/')
    def comment_add(self, request, **kwargs):
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        post = get_object_or_404(Post, id=kwargs.get('post_id'))
        self.check_object_permissions(request, post.group)
        serializer.save(owner=request.user, post=post)
        return JsonResponse(data=serializer.data, status=201, safe=False)

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        group_or_post_or_comment_owner_actions = ['comment_delete']
        group_owner_or_post_owner_actions = ['delete_post', 'comment_delete']
        post_owner_actions = ['delete_post', 'edit_post', 'comment_delete', 'comment_edit']
        group_member_actions = ['create_post', 'posts_list', 'post_detail', 'comment_add']
        if self.action in group_or_post_or_comment_owner_actions:
            self.permission_classes.append(IsGroupOrPostOrCommentOwner)
        elif self.action in group_owner_or_post_owner_actions:
            self.permission_classes.append(IsGroupOrPostOwner)
        elif self.action in post_owner_actions:
            self.permission_classes.append(IsObjOwner)
        elif self.action in group_member_actions:
            self.permission_classes.append(IsGroupMember)
        return [permission() for permission in self.permission_classes]
