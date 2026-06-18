"""Права доступа для пользователей и контента."""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request, view):
        """Проверяет, что пользователь аутентифицирован и является админом."""
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает чтение всем, а изменение только администраторам."""

    def has_permission(self, request, view):
        """Проверяет права для безопасных и небезопасных запросов."""
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Разрешает изменение автору, модератору или администратору."""

    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к конкретному объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    obj.author == request.user
                    or request.user.is_moderator
                    or request.user.is_admin
                )
            )
        )
