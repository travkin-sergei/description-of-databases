# app_services/permissions.py
from rest_framework import permissions


class IsAdminUser(permissions.IsAdminUser):
    """
    Разрешает доступ только пользователям с флагом is_staff=True.
    Используется для административных действий.
    """
    pass


class IsEditor(permissions.BasePermission):
    """
    Разрешает доступ пользователям с ролью «Редактор».
    Предполагается, что у модели User есть метод или поле, определяющее роль.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Пример проверки через атрибут/метод пользователя
            # Замените на реальную логику определения роли
            return request.user.has_role('editor') or request.user.is_staff
        return False


class IsReader(permissions.BasePermission):
    """
    Разрешает доступ всем аутентифицированным пользователям (чтение).
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanModifyTableGroup(permissions.BasePermission):
    """
    Разрешает создание/изменение/удаление TableGroup:
    - администраторам (is_staff);
    - редакторам с соответствующей ролью.
    """

    def has_object_permission(self, request, view, obj):
        # Для новых объектов (создание)
        if view.action == 'create':
            return request.user.is_staff or request.user.has_role('editor')

        # Для изменения/удаления — проверка прав на конкретный объект
        # Здесь можно добавить логику на основе полей объекта (например, ownership)
        return request.user.is_staff or request.user.has_role('editor')

    def has_permission(self, request, view):
        # Базовая проверка для всех действий
        return request.user and request.user.is_authenticated


class CanModifyColumnGroup(permissions.BasePermission):
    """
    Аналогично CanModifyTableGroup, но для ColumnGroup.
    """

    def has_object_permission(self, request, view, obj):
        if view.action == 'create':
            return request.user.is_staff or request.user.has_role('editor')
        return request.user.is_staff or request.user.has_role('editor')

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает:
    - полный доступ владельцу объекта;
    - только чтение для остальных аутентифицированных пользователей.
    Предполагает наличие поля `owner` у модели.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение всегда разрешено для аутентифицированных
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменение/удаление — только владельцу
        return obj.owner == request.user


class HasRole(permissions.BasePermission):
    """
    Проверка наличия конкретной роли у пользователя.
    Пример использования: permission_classes = [HasRole]
    и передача роли через `role_name` в kwargs представления.
    """

    def has_permission(self, request, view):
        role_name = view.kwargs.get('role_name')  # Или другой способ передачи
        if not role_name:
            return False
        return request.user and request.user.is_authenticated and request.user.has_role(role_name)

