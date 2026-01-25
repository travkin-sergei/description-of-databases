# app_url/permissions.py
from rest_framework import permissions


class DimUrlPermission(permissions.BasePermission):
    """
    Кастомизированное разрешение для модели DimUrl.

    Определяет правила доступа к объектам DimUrl в зависимости от метода запроса и роли пользователя.
    """

    def has_permission(self, request, view):
        """
        Проверяет общие права на доступ к эндпоинту (до проверки конкретного объекта).

        Args:
            request: HTTP-запрос.
            view: представление (ViewSet/APIView), обрабатывающее запрос.

        Returns:
            bool: True, если доступ разрешён; False — иначе.
        """
        # Все пользователи могут выполнять безопасные методы (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для методов записи (POST, PUT, PATCH, DELETE) требуется аутентификация
        if not request.user or not request.user.is_authenticated:
            return False

        # Админы могут выполнять любые действия
        if request.user.is_staff:
            return True

        # Обычные пользователи могут:
        # - создавать новые записи (POST)
        # - обновлять свои записи (PUT/PATCH), если логика приложения это позволяет
        # - не могут удалять записи (DELETE)
        if request.method == 'POST':
            return True
        if request.method in ['PUT', 'PATCH']:
            # Для обновления потребуется дополнительная проверка на уровне объекта (has_object_permission)
            return True
        if request.method == 'DELETE':
            return False

        return False

    def has_object_permission(self, request, view, obj):
        """
        Проверяет права на доступ к конкретному объекту DimUrl.

        Args:
            request: HTTP-запрос.
            view: представление, обрабатывающее запрос.
            obj: экземпляр модели DimUrl, к которому идёт обращение.

        Returns:
            bool: True, если доступ разрешён; False — иначе.
        """
        # Безопасные методы доступны всем аутентифицированным пользователям
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Админы могут выполнять любые действия с любым объектом
        if request.user.is_staff:
            return True

        # Для обычных пользователей:
        # - Обновление (PUT/PATCH) разрешено, если пользователь связан с объектом
        #   (например, через поле owner, если таковое есть в модели)
        # - Удаление (DELETE) запрещено
        if request.method in ['PUT', 'PATCH']:
            # Пример проверки: если у модели есть поле owner
            # return obj.owner == request.user
            # Если логика приложения не предполагает владельца, можно разрешить обновление всем аутентифицированным
            return True

        if request.method == 'DELETE':
            return False

        return False


class ReadOnlyForAnonymous(permissions.BasePermission):
    """
    Разрешает:
    - Анонимным пользователям — только чтение (GET).
    - Авторизованным пользователям — полный доступ.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ:
    - Владельцу объекта (поле owner == request.user) — полный доступ.
    - Админам (is_staff=True) — полный доступ.
    - Остальным — только чтение.

    Предполагается, что модель имеет поле owner.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем аутентифицированным пользователям
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        # Полный доступ: владельцу или админу
        return (
                (hasattr(obj, 'owner') and obj.owner == request.user) or
                request.user.is_staff
        )
