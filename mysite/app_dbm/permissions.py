from rest_framework import permissions



class IsDBA(permissions.BasePermission):
    """
    Разрешает доступ только пользователям с группой 'DBA' (администраторы баз данных).
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='DBA').exists()



class IsDeveloper(permissions.BasePermission):
    """
    Разрешает доступ пользователям с группой 'Developer' (разработчики).
    Обычно только чтение.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Developer').exists()



class IsAnalyst(permissions.BasePermission):
    """
    Разрешает доступ пользователям с группой 'Analyst' (аналитики).
    Только чтение метаданных.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Analyst').exists()



class CanCreateTotalData(permissions.BasePermission):
    """
    Разрешает создание записей в TotalData:
    - пользователям из группы 'DBA';
    - суперпользователям.
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True  # Другие методы проверяются отдельно
        return (
            request.user.is_superuser or
            request.user.groups.filter(name='DBA').exists()
        )



class CanUpdateTotalData(permissions.BasePermission):
    """
    Разрешает обновление записей в TotalData только DBA.
    Запрещает изменение ключевых полей (влияющих на хэш).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return (
                request.user.is_superuser or
                request.user.groups.filter(name='DBA').exists()
            )
        return True



class CanDeleteTotalData(permissions.BasePermission):
    """
    Разрешает удаление записей в TotalData только суперпользователям или DBA.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or
            request.user.groups.filter(name='DBA').exists()
        )



class ReadOnlyForAnalysts(permissions.BasePermission):
    """
    Разрешает только чтение (GET) для аналитиков.
    Запрещает POST/PUT/PATCH/DELETE.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return self.has_read_permission(request, view)
        return False

    def has_read_permission(self, request, view):
        return request.user.groups.filter(name='Analyst').exists()



class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Разрешает:
    - всем — чтение (GET, HEAD, OPTIONS);
    - только суперпользователям — запись (POST, PUT, PATCH, DELETE).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser



# Комбинированные разрешения для TotalDataViewSet
class TotalDataPermissions(permissions.BasePermission):
    """
    Комплексное разрешение для TotalDataViewSet:
    - GET: все аутентифицированные пользователи;
    - POST: DBA или суперпользователь;
    - PUT/PATCH: только DBA или суперпользователь;
    - DELETE: только суперпользователь.
    """
    def has_permission(self, request, view):
        # Все аутентифицированные могут читать
        if request.method == 'GET':
            return request.user and request.user.is_authenticated

        # POST: только DBA или суперпользователь
        if request.method == 'POST':
            return (
                request.user.is_superuser or
                request.user.groups.filter(name='DBA').exists()
            )

        # PUT/PATCH: только DBA или суперпользователь
        if request.method in ['PUT', 'PATCH']:
            return (
                request.user.is_superuser or
                request.user.groups.filter(name='DBA').exists()
            )

        # DELETE: только суперпользователь
        if request.method == 'DELETE':
            return request.user.is_superuser

        return False
