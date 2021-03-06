from django.http import JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from itertools import chain

from users.models import User
from users.serializers import UserSerializer
from .models import Group, PendingMembers
from rest_framework import viewsets, status
from .serializers import GroupSerializer, PendingMemberSerializer
from .permissions import IsAdminOrIsOwner, IsGroupMember, IsNotGroupMember


class GroupViewSet(viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(methods=['GET'], detail=False, url_name='details', url_path=r'(?P<pk>\d+)')
    def group_details(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        data = GroupSerializer(group, context={'host': request.get_host()}).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_name='create', url_path='create')
    def create_group(self, request, *args, **kwargs):
        serializer = GroupSerializer(data=request.data, context={'host': request.get_host()})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer.save(owner=request.user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=False, url_name='delete', url_path=r'(?P<pk>\d+)/delete')
    def delete_group(self, request, **kwargs):
        group = Group.objects.get(id=kwargs.get('pk'))
        self.check_object_permissions(request, group)
        group.delete()
        return Response(data={'message': "Group has been successfully deleted"})

    @action(methods=['PUT'], detail=False, url_name='update', url_path=r'(?P<pk>\d+)/update')
    def update_group(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        self.check_object_permissions(request, group)
        serializer = GroupSerializer(group, request.data, partial=True, context={'host': request.get_host()})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer.update(group, serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_name='join', url_path=r'(?P<pk>\d+)/join')
    def join_group(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        self.check_object_permissions(request, group)
        try:
            PendingMembers.objects.get(user=request.user, group=group)
            return Response(data={'message': 'You are already on waiting list!'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        except PendingMembers.DoesNotExist:
            PendingMembers.objects.create(group=group, user=request.user)
            return Response(data={'message': 'You successfully signed in to waiting list! '},
                            status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=False, url_name='manage', url_path=r'(?P<pk>\d+)/manage')
    def manage_pending_user(self, request, **kwargs):
        user = get_object_or_404(User, id=request.data['id'])
        pending = get_object_or_404(PendingMembers, group__id=kwargs.get('pk'), user=user)
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        self.check_object_permissions(request, group)
        message = 'Successfully declined'
        if request.method == 'POST':
            group.members.add(pending.user)
            message = 'Successfully accepted'
        pending.delete()
        return JsonResponse(data={'message': message}, status=200)

    @action(methods=['GET'], detail=False, url_name='my_groups', url_path='my_groups')
    def groups_list(self, request):
        groups = list(chain([*Group.objects.filter(members=request.user), *Group.objects.filter(owner=request.user)]))
        if len(groups) == 0:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={'message': 'You have no groups yet.'})
        response_groups = GroupSerializer(groups, context={'host': request.get_host()}, many=True).data
        paginator = PageNumberPagination()
        data = paginator.paginate_queryset(response_groups, request)
        return paginator.get_paginated_response(data=data)

    @action(methods=['POST'], detail=False, url_name='search', url_path='search')
    def search_for_group(self, request):

        if request.data.get('phrase'):
            phrase = request.data.get('phrase')
            groups = Group.objects.filter(name__contains=phrase)
        else:
            phrase = '  '
            groups = Group.objects.all()

        if len(phrase) < 2:
            return Response(data={'message': 'You provided too short search phrase'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        response_groups = GroupSerializer(groups, context={'host': request.get_host()}, many=True).data
        data = paginator.paginate_queryset(response_groups, request)
        if len(data) == 0:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={'message': 'No groups were found'})
        return paginator.get_paginated_response(data=data)

    @action(methods=['POST'], detail=False, url_name='leave', url_path=r'(?P<pk>\d+)/leave')
    def leave_group(self, request, **kwargs):
        group = get_object_or_404(
            Group, members=request.user, id=kwargs.get('pk'))
        group.members.remove(request.user)
        return Response(data={'message': 'You successfully left this group.'}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_name='pending_list', url_path=r'(?P<pk>\d+)/pending')
    def pending_list(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        self.check_object_permissions(request, group)
        pendings = PendingMemberSerializer(PendingMembers.objects.filter(group=group),
                                           context={'host': request.get_host()}, many=True).data
        if len(pendings) == 0:
            return Response(data={'message': 'Here is no pending member'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        paginator = PageNumberPagination()
        data = paginator.paginate_queryset(pendings, request)
        return paginator.get_paginated_response(data=data)

    @action(methods=['POST'], detail=False, url_name='member_list', url_path=r'(?P<pk>\d+)/members')
    def member_list(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        self.check_object_permissions(request, group)
        members = UserSerializer(group.members, many=True, context={'host': request.get_host()}).data
        return JsonResponse(data=members, status=200, safe=False)

    @action(methods=['POST'], detail=False, url_name='foreign_details', url_path=r'(?P<pk>\d+)/foreign')
    def foreign_group_details(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        if request.user in group.members.all():
            return Response(data={'message': 'You are a member yet'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        group_details = GroupSerializer(group, context={'host': request.get_host()}).data
        return Response(data=group_details, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_name='foreign_details', url_path=r'(?P<pk>\d+)/is_owner')
    def is_group_owner(self, request, **kwargs):
        group = get_object_or_404(Group, id=kwargs.get('pk'))
        if request.user == group.owner:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    def get_permissions(self):
        admin_or_group_owner_actions = [
            'delete_group', 'update_group', 'accept_pending_user', 'pending_list']
        group_member_actions = ['member_list']
        not_member_actions = ['join_group']
        self.permission_classes = [IsAuthenticated]
        if self.action in admin_or_group_owner_actions:
            self.permission_classes.append(IsAdminOrIsOwner)
        elif self.action in group_member_actions:
            self.permission_classes.append(IsGroupMember)
        elif self.action in not_member_actions:
            self.permission_classes.append(IsNotGroupMember)
        return [permission() for permission in self.permission_classes]
