from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """Права пользователя на запрос к объектам пользователям."""

    def has_permission(self, request, view):
        return request.method in ('POST') or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj or request.user.is_superuser


class PostCommentPermisson(permissions.BasePermission):
    """Права пользователя на запрос к объектам постам."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_superuser
        )
