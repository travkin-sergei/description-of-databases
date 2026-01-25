# app_updates/permissions.py
from rest_framework import permissions


class GetOnlyWithoutAuth(permissions.BasePermission):
    """
    Разрешает выполнение безопасных HTTP‑методов (GET, HEAD, OPTIONS) без аутентификации.
    Запрещает все небезопасные методы (POST, PUT, PATCH, DELETE).

    Использование:
    - Подходит для открытых API с чтением данных.
    - Комбинировать с другими разрешениями через `&` (AND) или `|` (OR) при необходимости.
    """

    def has_permission(self, request, view):
        """
        Проверяет, разрешён ли запрос текущему пользователю.

        Args:
            request: объект запроса DRF.
            view: экземпляр представления, обрабатывающего запрос.

        Returns:
            bool: True, если метод безопасен (GET/HEAD/OPTIONS); False для остальных.
        """
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запрещаем все остальные методы (POST, PUT, PATCH, DELETE)
        return False

    def has_object_permission(self, request, view, obj):
        """
        Проверяет разрешение на уровне объекта.

        Для согласованности с `has_permission` применяет ту же логику:
        - безопасные методы → разрешены;
        - остальные → запрещены.

        Args:
            request: объект запроса.
            view: представление.
            obj: объект модели (не используется в логике).

        Returns:
            bool: результат проверки.
        """
        return self.has_permission(request, view)


# Пример использования в ViewSet
"""
class PublicDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PublicData.objects.all()
    serializer_class = PublicDataSerializer
    permission_classes = [GetOnlyWithoutAuth]
"""
