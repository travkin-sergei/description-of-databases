# app_dict/permissions.py
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Разрешает доступ только пользователям с правами администратора (is_staff).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsDBA(permissions.BasePermission):
    """
    Разрешает доступ только пользователям из группы "DBA".
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='DBA').exists()


class IsAnalyst(permissions.BasePermission):
    """
    Разрешает доступ только пользователям из группы "Analyst".
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Analyst').exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает:
    - Чтение (GET, HEAD, OPTIONS) — всем.
    - Запись (POST, PUT, PATCH, DELETE) — только владельцу объекта.

    Предполагает, что у модели есть поле `user` или `owner`, ссылающееся на User.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для записи проверяем, что объект принадлежит пользователю
        # Предполагаем, что у объекта есть поле `owner` или `user`
        owner_field = getattr(obj, 'owner', None) or getattr(obj, 'user', None)
        return owner_field == request.user


class ReadOnly(permissions.BasePermission):
    """
    Только чтение (GET, HEAD, OPTIONS).
    Запрещает любые изменения (POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AllowAny(permissions.BasePermission):
    """
    Полный доступ (по умолчанию в DRF).
    """

    def has_permission(self, request, view):
        return True


class DenyAll(permissions.BasePermission):
    """
    Запрещает любой доступ.
    Полезно для временного отключения эндпоинта.
    """

    def has_permission(self, request, view):
        return False


class CustomPermission(permissions.BasePermission):
    """
    Пример кастомного разрешения с логикой по условиям.
    Можно адаптировать под свои правила.
    """

    def has_permission(self, request, view):
        # Пример: доступ только в рабочие часы (9:00–18:00)
        from datetime import time
        current_time = request.datetime.now().time()
        if time(9, 0) <= current_time <= time(18, 0):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Дополнительная проверка на уровне объекта
        return obj.is_published
