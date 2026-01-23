from rest_framework import permissions


class GetOnlyWithoutAuth(permissions.BasePermission):
    """
    Разрешает все GET, HEAD, OPTIONS запросы без аутентификации.
    Все остальные методы (POST, PUT, PATCH, DELETE) запрещены.
    """

    def has_permission(self, request, view):
        # Разрешаем только безопасные методы
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        # Все остальные методы запрещены
        return False
