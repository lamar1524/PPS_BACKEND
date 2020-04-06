from rest_framework import permissions

from groups.models import Group
from posts.models import Comment


class IsAdmin(permissions.BasePermission):
    message = 'This action is allowed only for admins'

    def has_permission(self, request, view):
        return request.user.is_admin


class IsObjOwner(permissions.BasePermission):
    message = "This action is allowed only for post's owner"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsGroupMember(permissions.BasePermission):
    message = "This action is allowed only for group's member"

    def has_object_permission(self, request, view, obj):
        return (request.user in obj.members.all()) or request.user == obj.owner


class IsGroupOrPostOwner(permissions.BasePermission):
    message = "This action is allowed only for group's, or post's owner"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user == obj.group.owner


class IsGroupOrPostOrCommentOwner(permissions.BasePermission):
    message = "To do this, you need to be owner of at leas one of the following: group, post, comment"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.post.owner == request.user or obj.post.group.owner == request.user
