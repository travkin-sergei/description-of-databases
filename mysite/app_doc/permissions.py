# app_doc/permissions.py
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Разрешает доступ только администраторам (is_staff=True).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsEditor(permissions.BasePermission):
    """
    Разрешает доступ пользователям из группы "Редактор".
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Редактор').exists()


class IsReader(permissions.BasePermission):
    """
    Разрешает доступ пользователям из группы "Читатель".
    Только чтение (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name='Читатель').exists()
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает:
    - Администраторам — полный доступ.
    - Владельцу объекта — редактирование и удаление.

    Предполагает, что у модели есть поле `owner` или `created_by`, ссылающееся на User.
    """

    def has_object_permission(self, request, view, obj):
        # Администраторы имеют полный доступ
        if request.user.is_staff:
            return True

        # Для остальных проверяем владение объектом
        owner_field = getattr(obj, 'owner', None) or getattr(obj, 'created_by', None)
        return owner_field == request.user


class CanModifyDoc(permissions.BasePermission):
    """
    Разрешает изменение/удаление документа только если:
    - Пользователь — администратор, ИЛИ
    - Документ не помечен как "архивный" (is_archived=False).
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if hasattr(obj, 'is_archived') and obj.is_archived:
            return False

        return True


class ReadOnly(permissions.BasePermission):
    """
    Только чтение (GET, HEAD, OPTIONS). Запрещает любые изменения.
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
    Запрещает любой доступ. Полезно для временного отключения эндпоинта.
    """

    def has_permission(self, request, view):
        return False


class CustomDocPermission(permissions.BasePermission):
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
        # Дополнительная проверка: документ не должен быть просрочен
        if obj.date_stop and obj.date_stop < request.datetime.now().date():
            return False
        return True
