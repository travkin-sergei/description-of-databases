# app_request/permissions.py

from rest_framework import permissions


class IsAdminOrEditor(permissions.BasePermission):
    """
    Разрешает доступ, если пользователь:
    - Администратор (is_staff=True) ИЛИ
    - Находится в группе 'Редактор'
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
                request.user.is_staff or
                request.user.groups.filter(name='Редактор').exists()
        )


class IsReader(permissions.BasePermission):
    """
    Разрешает доступ только для чтения (GET, HEAD, OPTIONS)
    пользователям из группы 'Читатель'.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name='Читатель').exists()
        return False
