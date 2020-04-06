from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    message = 'This action is allowed only for admins'

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrIsOwner(permissions.BasePermission):
    message = "This action is allowed only for group's admin"

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_admin


class IsGroupMember(permissions.BasePermission):
    message = "This action is allowed only for group's member"

    def has_object_permission(self, request, view, obj):
        return (obj.owner == request.user) or (request.user in obj.members.all())


class IsNotGroupMember(permissions.BasePermission):
    message = "To do this, you mustn't be in this group"

    def has_object_permission(self, request, view, obj):
        return not (obj.owner == request.user) and (request.user not in obj.members.all())
