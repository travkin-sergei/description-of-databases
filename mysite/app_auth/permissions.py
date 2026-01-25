# app_auth/permissions.py
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только владелец объекта может редактировать.
    Для профиля пользователя — только свой профиль.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class CanManageRegistrationRequests(permissions.BasePermission):
    """
    Только администраторы или суперпользователи могут управлять заявками.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff